// index.js
const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const iconv = require('iconv-lite');
const app = express();
const PORT = 5000;


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
  
      $('table.type_2 tbody tr').each((index, element) => {
        const name = $(element).find('td:nth-child(2) a').text().trim();
        const price = $(element).find('td:nth-child(3)').text().trim();
        const change = $(element).find('td:nth-child(5)').text().trim();
        const marketCap = $(element).find('td:nth-child(7)').text().trim();
  
        if (name && stockList.length < 100) {
          stockList.push({
            rank: index + 1,
            name,
            price,
            change,
            color: change.includes('+') ? 'red' : change.includes('-') ? 'blue' : 'gray',
            image: `/${name[0]}.png`,
          });
        }
      });
  
      res.json(stockList);
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
