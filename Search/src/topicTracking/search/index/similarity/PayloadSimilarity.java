package topicTracking.search.index.similarity;

import org.apache.lucene.analysis.payloads.PayloadHelper;
import org.apache.lucene.index.FieldInvertState;
import org.apache.lucene.search.DefaultSimilarity;

public class PayloadSimilarity extends DefaultSimilarity {

	private static final long serialVersionUID = 1L;

	@Override
	public float scorePayload(int docId, String fieldName, int start, int end,
			byte[] payload, int offset, int length) {
		return PayloadHelper.decodeFloat(payload, offset);
	}
	
	// TODO: previously, lengthNorm was overridden
	
	@Override
	public float computeNorm(String field, FieldInvertState state) {
	    @SuppressWarnings("unused")
		final int numTerms;
	    if (discountOverlaps)
	      numTerms = state.getLength() - state.getNumOverlap();
	    else
	      numTerms = state.getLength();
	    // return state.getBoost() * ((float) (1.0 / Math.sqrt(numTerms)));
	    return state.getBoost();
	  }

}
