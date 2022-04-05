import edu.uci.ics.crawler4j.crawler.Page;
import edu.uci.ics.crawler4j.crawler.WebCrawler;
import edu.uci.ics.crawler4j.parser.HtmlParseData;
import edu.uci.ics.crawler4j.url.WebURL;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Set;
import java.util.regex.Pattern;

// Класс краулера
public class HtmlCrawler extends WebCrawler {

    private final static Pattern EXCLUSIONS
            = Pattern.compile(".*(\\.(css|js|xml|gif|jpg|png|mp3|mp4|zip|gz|pdf))$");

    static int count = 0;
    static ArrayList<String> urlList = new ArrayList<>();

    //Метод для определения, на какой сайт перейти
    @Override
    public boolean shouldVisit(Page referringPage, WebURL url) {
        String urlString = url.getURL().toLowerCase();
        return !EXCLUSIONS.matcher(urlString).matches()
                && urlString.startsWith("https://startandroid.ru/");
    }

    // Переходим на страницу, берем ее html код и записываем в файл
    @Override
    public void visit(Page page) {
        String url = page.getWebURL().getURL();

        if (page.getParseData() instanceof HtmlParseData) {
            HtmlParseData htmlParseData = (HtmlParseData) page.getParseData();
            String html = htmlParseData.getHtml();
            count++;
            try {
                PrintWriter writer = new PrintWriter("D:\\IdeaProjects\\WebParser\\src\\pages\\" + count + ".txt", "UTF-8");
                writer.println(html);
                writer.close();
                urlList.add(url);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
