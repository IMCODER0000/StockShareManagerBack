// index.js
const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const iconv = require('iconv-lite');
const yahooFinance = require('yahoo-finance2').default;
const { spawn } = require('child_process');
const cors = require('cors');
const app = express();
const PORT = 4000;

app.use(cors()); 
app.use(express.json());

// 시가총액 문자열을 숫자로 변환하는 함수
function parseMarketCap(marketCapStr) {
  // 문자열에서 콤마(,) 제거
  const cleanedStr = marketCapStr.replace(/,/g, '');

  // 숫자 변환 시, 빈 문자열이면 0 반환
  const value = parseFloat(cleanedStr) || 0;
  return value;
}



app.get('/api/stocks', async (req, res) => {
  try {
    // EUC-KR 인코딩된 데이터 요청
    const response = await axios.get('https://finance.naver.com/sise/sise_market_sum.nhn?sosok=0', {
      responseType: 'arraybuffer',
    });

    // 인코딩 변환 (EUC-KR -> UTF-8)
    const decodedData = iconv.decode(response.data, 'EUC-KR');
    const $ = cheerio.load(decodedData);
    const stockList = [];

    // 테이블에서 데이터 파싱
    $('table.type_2 tbody tr').each((index, element) => {
      const name = $(element).find('td:nth-child(2) a').text().trim();
      const price = $(element).find('td:nth-child(3)').text().trim();
      const change = $(element).find('td:nth-child(5)').text().trim();
      const marketCapStr = $(element).find('td:nth-child(7)').text().trim();

      // 주식의 ticker (a 태그에서 href 속성 추출)
      const href = $(element).find('td:nth-child(2) a').attr('href');
      const ticker = href ? href.match(/code=([0-9]+)/) : null;
      const tickerCode = ticker ? ticker[1] : null;

      // 시가총액 문자열을 숫자로 변환 (단위는 억 원)
      const marketCap = parseMarketCap(marketCapStr);

      // 데이터가 존재할 때만 추가
      if (name && marketCap > 0 && tickerCode) {
        stockList.push({
          name,
          price,
          change,
          marketCap: marketCapStr,
          ticker: tickerCode,  // tickerCode 추가
          color: change.includes('+') ? 'red' : change.includes('-') ? 'blue' : 'gray',
          image: `/${name[0]}.png`,
        });
      }
    });

    // 시가총액 기준 내림차순 정렬
    stockList.sort((a, b) => b.marketCap - a.marketCap);

    // 랭킹 지정
    const rankedList = stockList.map((stock, index) => ({
      rank: index + 1,
      ...stock,
    }));

    res.json(rankedList);
    console.log("Data Send Success");
  } catch (error) {
    console.error(error);
    res.status(500).send('Error fetching stock data');
  }
});

app.get('/api/stocks/:ticker/history', async (req, res) => {
  const ticker = req.params.ticker; // 종목 코드

  try {
    // 현재 날짜
    const endDate = new Date();
    // 5년 전 날짜
    const startDate = new Date();
    startDate.setFullYear(endDate.getFullYear() - 5);

    // Unix Timestamp로 변환
    const period1 = Math.floor(startDate.getTime() / 1000);
    const period2 = Math.floor(endDate.getTime() / 1000);

    // `chart` 메서드 사용
    const options = {
      period1,
      period2,
      interval: '3mo', // 1개월 간격 데이터
    };

    const data = await yahooFinance.chart(ticker, options);

    res.json(data);
    console.log(`Data for ticker ${ticker} fetched successfully`);
  } catch (error) {
    console.error('Error fetching historical stock data:', error.message);
    res.status(500).send('Error fetching historical stock data');
  }
});


app.get('/api/stocks/:ticker/history2', async (req, res) => {
  const ticker = req.params.ticker; // 종목 코드

  try {
    // 현재 날짜
    const endDate = new Date();
    // 7일 전 날짜
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - 7); // 7일 전 날짜로 설정

    // Unix Timestamp로 변환
    const period1 = Math.floor(startDate.getTime() / 1000);
    const period2 = Math.floor(endDate.getTime() / 1000);

    // `chart` 메서드 사용
    const options = {
      period1,
      period2,
      interval: '1d', // 1일 간격 데이터
    };

    const data = await yahooFinance.chart(ticker, options);

    res.json(data);
    console.log(`Data for ticker ${ticker} fetched successfully`);
  } catch (error) {
    console.error('Error fetching historical stock data:', error.message);
    res.status(500).send('Error fetching historical stock data');
  }
});


app.post('/api/runPython', (req, res) => {
  const { company1, company2, company3, totalInvestment, risk } = req.body;

  if (!company1 || !company2 || !company3 || !totalInvestment || !risk) {
    return res.status(400).send('모든 파라미터가 필요합니다.');
  }
  console.log("###########2 : ", company1, company2, company3, totalInvestment, risk);

  // Python 스크립트 실행
  const pythonProcess = spawn('python', ['a.py', company1, company2, company3, totalInvestment, risk]);

  console.log("########### : ", 'python', ['a.py', company1, company2, company3, totalInvestment, risk])

  let output = '';

  // Python 스크립트 출력 처리
  pythonProcess.stdout.on('data', (data) => {
    output += data.toString();
  });


  // 에러 처리
  pythonProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  // Python 프로세스가 종료되면
  pythonProcess.on('close', (code) => {
    if (code === 0) {
      // 출력값을 객체로 파싱
      const parsedOutput = parsePythonOutput(output);

      // 객체 형태로 리액트로 응답
      res.json(parsedOutput);
    } else {
      res.status(500).send(`Python process exited with code ${code}`);
    }
  });
});

// Python 출력 파싱 함수
function parsePythonOutput(output) {
  const regex = /(\D+)\s+투자\s+금액:\s+([\d,]+)/g;
  const result = {};

  // 전체 투자 금액, rf 등의 값 추출
  const totalRegex = /총\s+투자\s+금액\s+:\s+([\d,]+)/;
  const rfRegex = /rf\s+:\s+([\d,]+)/;

  const totalMatch = output.match(totalRegex);
  const rfMatch = output.match(rfRegex);

  if (totalMatch) result.total = parseInt(totalMatch[1].replace(/,/g, ''));
  if (rfMatch) result.rf = parseInt(rfMatch[1].replace(/,/g, ''));

  let match;
  while ((match = regex.exec(output)) !== null) {
    const companyName = match[1].trim();
    const investmentAmount = parseInt(match[2].replace(/,/g, '')); // 쉼표 제거
    result[companyName] = investmentAmount;
  }
  
  return result;
}


app.get('/runPython', (req, res) => {
  // URL에서 파라미터 추출
  const { company1, company2, company3, totalInvestment, risk } = req.params;

  if (!company1 || !company2 || !company3 || !totalInvestment || !risk) {
    return res.status(400).send('모든 파라미터가 필요합니다.');
  }

  // Python 스크립트 실행
  const pythonProcess = spawn('python', ['a.py', company1, company2, company3, totalInvestment, risk]);

  let output = '';

  // Python 스크립트 출력 처리
  pythonProcess.stdout.on('data', (data) => {
    output += data.toString();
  });

  // 에러 처리
  pythonProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  // Python 프로세스가 종료되면
  pythonProcess.on('close', (code) => {
    if (code === 0) {
      // 출력값을 반환
      res.send(output);
    } else {
      res.status(500).send(`Python process exited with code ${code}`);
    }
  });
});
app.get('/api/ai/:name', (req, res) => {

  const name = req.params.name;


 
  let pythonProcess = spawn('python', ['samsung.py'], { cwd: './tmp' });

  if(name === "SK하이닉스"){
    console.log('하이닉스 시작');
    pythonProcess = spawn('python', ['sk.py'], { cwd: './tmp' });
  }

 

  let output = '';

  // Python 스크립트 stdout 데이터 수집
  pythonProcess.stdout.on('data', (data) => {
    console.log('Python Output:', data.toString());
    output += data.toString();
  });

  // Python 스크립트 stderr 데이터 처리
  pythonProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  // Python 스크립트 종료 후 클라이언트에 응답
  pythonProcess.on('close', (code) => {
    if (code === 0) {
      // 출력값에서 줄바꿈 등 불필요한 공백 제거
      const trimmedOutput = output.trim();
      console.log('Trimmed Output:', trimmedOutput);
      
      // 출력값이 정상적으로 숫자인지 확인
      const price = parseFloat(trimmedOutput);
      console.log('Parsed Price:', price);

      if (isNaN(price)) {
        res.status(500).send("가격 정보가 잘못되었습니다.");
      } else {
        // 가격을 JSON 형식으로 반환
        res.json({ price });
      }
    } else {
      res.status(500).send(`Python process exited with code ${code}`);
    }
  });
});




app.get('/', (req, res) => {
  res.send('Hello, World!');
});


app.get('/about', (req, res) => {
  res.send('About Page');
});


app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
