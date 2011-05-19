package topicTracking.search.index.similarity;

import org.elasticsearch.common.inject.Inject;
import org.elasticsearch.common.inject.assistedinject.Assisted;
import org.elasticsearch.common.settings.Settings;
import org.elasticsearch.index.AbstractIndexComponent;
import org.elasticsearch.index.Index;
import org.elasticsearch.index.settings.IndexSettings;
import org.elasticsearch.index.similarity.SimilarityProvider;

public class PayloadSimilarityProvider extends AbstractIndexComponent implements
		SimilarityProvider<PayloadSimilarity> {

	private PayloadSimilarity similarity;
	private String name;

	@Inject
	public PayloadSimilarityProvider(Index index,
			@IndexSettings Settings indexSettings,
			@Assisted Settings settings, @Assisted String name) {
		super(index, indexSettings, PayloadSimilarityProvider.class
				.getPackage().getName());
		this.name = name;
		this.similarity = new PayloadSimilarity();
	}

	@Override
	public PayloadSimilarity get() {
		return similarity;
	}

	@Override
	public String name() {
		return name;
	}
}
