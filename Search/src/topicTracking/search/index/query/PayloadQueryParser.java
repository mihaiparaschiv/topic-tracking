package topicTracking.search.index.query;

import static org.elasticsearch.index.query.support.QueryParsers.wrapSmartNameQuery;

import java.io.IOException;

import org.apache.lucene.index.Term;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.payloads.AveragePayloadFunction;
import org.apache.lucene.search.payloads.PayloadTermQuery;
import org.elasticsearch.common.inject.Inject;
import org.elasticsearch.common.settings.Settings;
import org.elasticsearch.common.xcontent.XContentParser;
import org.elasticsearch.index.AbstractIndexComponent;
import org.elasticsearch.index.Index;
import org.elasticsearch.index.mapper.MapperService;
import org.elasticsearch.index.query.QueryParsingException;
import org.elasticsearch.index.query.xcontent.QueryParseContext;
import org.elasticsearch.index.query.xcontent.XContentQueryParser;
import org.elasticsearch.index.settings.IndexSettings;

public class PayloadQueryParser extends AbstractIndexComponent implements
		XContentQueryParser {

	public static final String NAME = "payload";

	@Inject
	public PayloadQueryParser(Index index, @IndexSettings Settings settings) {
		super(index, settings, PayloadQueryParser.class.getPackage().getName());
	}

	@Override
	public String[] names() {
		return new String[] { NAME };
	}

	@Override
	public Query parse(QueryParseContext parseContext) throws IOException,
			QueryParsingException {
		XContentParser parser = parseContext.parser();

		XContentParser.Token token = parser.nextToken();
		assert token == XContentParser.Token.FIELD_NAME;
		String fieldName = parser.currentName();

		String value = null;
		float boost = 1.0f;
		token = parser.nextToken();
		if (token == XContentParser.Token.START_OBJECT) {
			String currentFieldName = null;
			while ((token = parser.nextToken()) != XContentParser.Token.END_OBJECT) {
				if (token == XContentParser.Token.FIELD_NAME) {
					currentFieldName = parser.currentName();
				} else {
					if ("term".equals(currentFieldName)) {
						value = parser.text();
					} else if ("value".equals(currentFieldName)) {
						value = parser.text();
					} else if ("boost".equals(currentFieldName)) {
						boost = parser.floatValue();
					}
				}
			}
			parser.nextToken();
		} else {
			value = parser.text();
			// move to the next token
			parser.nextToken();
		}

		if (value == null) {
			throw new QueryParsingException(index,
					"No value specified for term query");
		}

		Query query = null;

		MapperService.SmartNameFieldMappers smartNameFieldMappers = parseContext
				.smartFieldMappers(fieldName);
		if (smartNameFieldMappers != null) {
			if (smartNameFieldMappers.hasMapper()) {
				fieldName = smartNameFieldMappers.mapper().names().indexName();
				value = smartNameFieldMappers.mapper().indexedValue(value);
			}
		}

		query = new PayloadTermQuery(new Term(fieldName, value),
				new AveragePayloadFunction());

		query.setBoost(boost);
		return wrapSmartNameQuery(query, smartNameFieldMappers, parseContext);
	}
}
