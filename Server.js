// index.js
const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const iconv = require('iconv-lite');
const cors = require('cors');
const app = express();
const PORT = 4000;

app.use(cors()); 

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


app.get('/', (req, res) => {
  res.send('Hello, World!');
});


app.get('/about', (req, res) => {
  res.send('About Page');
});


app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
