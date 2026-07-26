package Screener;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class FinvizScraper {

    public static Map<String, String> getStockData(String ticker) throws IOException {
        String url = "https://finviz.com/quote.ashx?t=" + ticker;
        Document doc = Jsoup.connect(url)
                            .userAgent("Mozilla/5.0")
                            .get();

        Elements table = doc.select(".snapshot-table2");
        Map<String, String> data = new HashMap<>();

        for (Element row : table.select("tr")) {
            Elements cells = row.select("td");
            for (int i = 0; i < cells.size(); i += 2) {
                String key = cells.get(i).text();
                String value = cells.get(i + 1).text();

                switch (key) {
                    case "Price": data.put("Price", value); break;
                    case "Change": data.put("Change", value); break;
                    case "Volume": data.put("Volume", value); break;
                    case "Avg Volume": data.put("Avg Vol", value); break;
                    case "Short Float": data.put("Float Short", value); break;
                    case "Short Ratio": data.put("Short Rat", value); break;
                    case "RSI (14)": data.put("RSI", value); break;
                    case "Rel Volume": data.put("Rel Vol", value); break;
                    case "Perf Month": data.put("Perf (M)", value); break;
                    case "Perf Week": data.put("Perf (W)", value); break;
                    case "Shs Float": data.put("Float", value); break;
                }
            }
        }

        return data;
    }
}
