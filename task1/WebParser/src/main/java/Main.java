import edu.uci.ics.crawler4j.crawler.CrawlConfig;
import edu.uci.ics.crawler4j.crawler.CrawlController;
import edu.uci.ics.crawler4j.fetcher.PageFetcher;
import edu.uci.ics.crawler4j.robotstxt.RobotstxtConfig;
import edu.uci.ics.crawler4j.robotstxt.RobotstxtServer;

import java.io.File;
import java.io.PrintWriter;

public class Main {
    public static void main(String[] args) throws Exception {
        //Настройка краулера
        File crawlStorage = new File("src/test/resources/crawler4j");
        CrawlConfig config = new CrawlConfig();
        config.setMaxPagesToFetch(120);

        config.setCrawlStorageFolder(crawlStorage.getAbsolutePath());

        int numCrawlers = 12;

        PageFetcher pageFetcher = new PageFetcher(config);
        RobotstxtConfig robotstxtConfig = new RobotstxtConfig();
        RobotstxtServer robotstxtServer = new RobotstxtServer(robotstxtConfig, pageFetcher);
        CrawlController controller = new CrawlController(config, pageFetcher, robotstxtServer);

        //Указываем сайт, с которого будем брать страницы
        controller.addSeed("https://startandroid.ru/");

        CrawlController.WebCrawlerFactory<HtmlCrawler> factory = HtmlCrawler::new;

        //Стартуем краулер
        controller.start(factory, numCrawlers);

        //Создаем файл index
        PrintWriter writer = new PrintWriter("D:\\IdeaProjects\\WebParser\\src\\pages\\" + "" + "index.txt" + "", "UTF-8");
        int index = 1;
        for (String s : HtmlCrawler.urlList) {
            writer.println(index + " -> " + s);
            index++;
        }
        writer.close();
    }
}
