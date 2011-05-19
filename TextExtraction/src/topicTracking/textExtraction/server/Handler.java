package topicTracking.textExtraction.server;

import java.io.StringReader;

import org.apache.thrift.TException;
import org.xml.sax.InputSource;

import topicTracking.service.textExtraction.TextExtractionService;
import de.l3s.boilerpipe.document.TextDocument;
import de.l3s.boilerpipe.extractors.ArticleExtractor;
import de.l3s.boilerpipe.sax.BoilerpipeSAXInput;

public class Handler implements TextExtractionService.Iface {
	@Override
	public String extract(String html) throws TException {
		try {
			// parse the HTML content
			InputSource is = new InputSource(new StringReader(html));
			BoilerpipeSAXInput in = new BoilerpipeSAXInput(is);
			TextDocument doc;
			doc = in.getTextDocument();

			// extract the text
			String text = ArticleExtractor.INSTANCE.getText(doc);
			
			return text;
		} catch (Exception e) {
			throw new TException(e);
		}
	}
}
