package topicTracking.search.index.analysis;

import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.payloads.DelimitedPayloadTokenFilter;
import org.apache.lucene.analysis.payloads.FloatEncoder;
import org.apache.lucene.analysis.payloads.PayloadEncoder;
import org.elasticsearch.common.inject.Inject;
import org.elasticsearch.common.inject.assistedinject.Assisted;
import org.elasticsearch.common.settings.Settings;
import org.elasticsearch.index.AbstractIndexComponent;
import org.elasticsearch.index.Index;
import org.elasticsearch.index.analysis.TokenFilterFactory;
import org.elasticsearch.index.settings.IndexSettings;

public class PayloadTokenFilterFactory extends AbstractIndexComponent implements
		TokenFilterFactory {

	private String name;
	private char delimiter;
	private PayloadEncoder payloadEncoder;

	@Inject
	public PayloadTokenFilterFactory(Index index,
			@IndexSettings Settings indexSettings, @Assisted Settings settings,
			@Assisted String name) {
		super(index, indexSettings, PayloadTokenFilterFactory.class
				.getPackage().getName());
		this.name = name;
		this.delimiter = '|';
		this.payloadEncoder = new FloatEncoder();
	}

	@Override
	public String name() {
		return name;
	}

	@Override
	public TokenStream create(TokenStream tokenStream) {
		return new DelimitedPayloadTokenFilter( //
				tokenStream, delimiter, payloadEncoder);
	}
}
