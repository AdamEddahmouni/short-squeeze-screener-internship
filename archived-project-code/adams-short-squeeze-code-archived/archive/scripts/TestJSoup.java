import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;

public class TestJSoup {
    public static void main(String[] args) throws Exception {
        Document doc = Jsoup.connect("https://finviz.com/quote.ashx?t=AAPL").get();
        System.out.println(doc.title());
    }
}