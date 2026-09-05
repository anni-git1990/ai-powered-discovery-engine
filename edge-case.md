# Edge Cases & Corner Scenarios Specification

This document details all potential edge cases, corner scenarios, data anomalies, and fail-safe handling strategies for the **AI-Powered Discovery Engine for Myntra Wishlist-to-Purchase Behavior**.

---

## 1. Data Ingestion & Source Platform Edge Cases

### 1.1 Code-Mixed Language (Hinglish & Regional Slang)
- **Scenario:** User comments written in Hinglish, Romanized Hindi, or colloquial Indian e-commerce terms:
  - *"Iska size thoda chota lag raha hai, pehne me comfortable hai kya?"*
  - *"Paisa vasool nahi hai, MRP badha ke discount diya hai."*
  - *"Sale ka wait kar rahi hu, 50% off pe lungi."*
- **Risk:** Standard English NLP models or basic LLM prompts misclassify intent or fail to parse blocker categories.
- **Handling Strategy:**
  - Inject explicit Hinglish/Romanized Hindi translation and domain slang mapping rules into system prompts for LLM agents.
  - Pre-filter text with a language detection module (`fasttext` / `langdetect`) and route code-mixed texts to Hinglish-aware model prompts.

### 1.2 Sarcasm, Irony & Inverse Sentiment
- **Scenario:** Sarcastic or ironical reviews where surface words contradict actual user experience:
  - *"Best shirt ever if you want a dishcloth after 1 wash!"*
  - *"Love how Myntra increased the price by ₹600 right before the 'Big Fashion Festival' sale!"*
- **Risk:** Sentiment classifiers score these as positive feedback (`HIGH_INTENT`, `NO_BLOCKER`).
- **Handling Strategy:**
  - Instruct the **Purchase Blocker Agent** to perform contradiction analysis between sentiment tone and outcome indicators.
  - Require agents to justify classifications with verbatim quote extraction, forcing model chain-of-thought validation.

### 1.3 High-Volume Bot Spam, Affiliate Links & Cross-Posting
- **Scenario:** Automated bots or affiliate marketers spamming repetitive comments across YouTube videos, Reddit threads, and Play Store reviews:
  - *"Use code DIS100 for extra ₹100 off on Myntra wishlist!"*
- **Risk:** Distorts frequency counts ($F$) in the Opportunity Scoring model.
- **Handling Strategy:**
  - Apply MinHash / LSH deduplication across cross-platform text vectors.
  - Filter posts containing external affiliate URLs, repetitive promotional regex patterns, or high posting frequency from a single author hash within 1 minute.

### 1.4 Short Snippets & Emoji-Only Comments
- **Scenario:** Extremely brief user input such as `"🔥"`, `"Size M"`, `"Not good"`, `"Waiting"`.
- **Risk:** Insufficient context produces hallucinated LLM classifications or vector embedding distortion.
- **Handling Strategy:**
  - Triage Agent enforces a minimum length threshold (e.g., `< 4 words` or `< 15 characters` without semantic keywords gets flagged as `INSUFFICIENT_CONTEXT` and excluded from scoring).

---

## 2. Wishlist Intent & Behavioral Ambiguity Edge Cases

### 2.1 Wishlist as a Pure Aesthetic Mood Board (Zero Purchase Intent)
- **Scenario:** Users wishlisting 100+ luxury/bridal items (e.g., designer lehengas worth ₹1,00,000+) with zero intent to purchase, treating Myntra like Pinterest or an aesthetic mood board.
- **Risk:** Engine flags expensive items as having massive "price friction" when the user never intended to buy.
- **Handling Strategy:**
  - **Wishlist Motivation Agent** evaluates contextual clues (e.g., *"Dream outfit"*, *"Bridal goals"*, *"Adding to my dream closet"*) and assigns them to `LOW_INTENT_BOOKMARKING` with intent score $\le 0.15$.
  - Exclude `LOW_INTENT_BOOKMARKING` items from purchase blocker opportunity scoring.

### 2.2 Shared Accounts & Multi-Persona Wishlisting
- **Scenario:** Family members or couples sharing a single Myntra account or device, wishlisting conflicting sizes (e.g., Men's L and Women's S) and contradictory style preferences.
- **Risk:** User Segmentation Agent gets confused by conflicting persona signals from the same author hash.
- **Handling Strategy:**
  - Segment feedback at the **individual post/comment level** rather than aggregating solely at the user account level.

### 2.3 Out-of-Stock & Discontinued Items
- **Scenario:** A user wishlists an item that goes out of stock or has limited size availability. User purchase intent remains high, but purchase is physically blocked by inventory, not hesitation.
- **Risk:** Misclassified as price or size uncertainty friction.
- **Handling Strategy:**
  - Separate `INVENTORY_STOCK_OUT` into a distinct logistical blocker category, preventing it from skewing product UX friction metrics.

### 2.4 Gifting & Event-Driven Wishlisting (Delayed Temporal Horizons)
- **Scenario:** A user wishlists an outfit for a wedding or festival 6 months away. The purchase is postponed due to event timing rather than product hesitation.
- **Risk:** Incorrectly classified as purchase abandonment.
- **Handling Strategy:**
  - Categorize temporal postponement under `EVENT_TIMING_POSTPONEMENT` within the Wishlist Motivation Agent.

---

## 3. AI Processing & Multi-Agent System Edge Cases

### 3.1 LLM Schema Constraint Violations & Malformed JSON
- **Scenario:** LLM outputs truncated JSON, invalid enum values, or wraps responses in markdown block ticks despite structured output instructions.
- **Risk:** Agent graph pipeline crashes due to Pydantic parsing errors.
- **Handling Strategy:**
  - Implement Pydantic output parsers with automatic retry logic (up to 3 retries with fallback formatting prompts).
  - Enforce JSON repair parsers (`json_repair` library) before raising parsing exceptions.

### 3.2 Conflicting Blocker Signals in a Single Comment
- **Scenario:** A single user comment mentions multiple distinct friction points:
  - *"Price is great, but size M feels like S, and the material looks super cheap compared to images."*
- **Risk:** Model arbitrarily picks one blocker, ignoring secondary friction points.
- **Handling Strategy:**
  - **Purchase Blocker Agent** extracts a `primary_blocker` AND a list of `secondary_blockers`.
  - Analytics engine weights primary blocker at 1.0 and secondary blockers at 0.5 in aggregate frequency metrics.

### 3.3 Evolving Gen-Z & Micro-Trend Vocabulary
- **Scenario:** Emerging fashion terms not present in initial training prompts (e.g., *"coquette aesthetic"*, *"gorpcore"*, *"old money style"*, *"clean girl fit"*).
- **Risk:** Triage agent flags valid fashion discussions as non-fashion noise.
- **Handling Strategy:**
  - Maintain a dynamic domain dictionary configuration file (`configs/fashion_taxonomy.json`) updated quarterly.
  - Use vector similarity search against ChromaDB seed taxonomy to resolve unknown terms to closest macro-categories.

### 3.4 Model Rate Limits (HTTP 429) & API Outages
- **Scenario:** Ingestion pipeline hits OpenAI/Anthropic rate limits or experiences service degradation during bulk processing of 50,000 comments.
- **Risk:** Ingestion job fails midway, leaving database in an inconsistent state.
- **Handling Strategy:**
  - Wrap API calls in `tenacity` retry logic with exponential backoff and jitter.
  - Implement checkpointing in DuckDB so batch ingestion can resume seamlessly from the last processed `post_id`.

---

## 4. Vector Embedding & Clustering Edge Cases

### 4.1 Polysemous Fashion Vocabulary & Semantic Drift
- **Scenario:** Words with multiple meanings in e-commerce context:
  - *"Drop"* $\rightarrow$ Price drop vs. waist drop vs. new collection drop.
  - *"Fit"* $\rightarrow$ Garment sizing fit vs. overall outfit ("nice fit").
- **Risk:** Cosine similarity in vector space clusters unrelated concepts together.
- **Handling Strategy:**
  - Provide surrounding contextual sentences when generating embeddings rather than embedding isolated words/phrases.

### 4.2 HDBSCAN Outlier Dominance (Cluster -1 Overflow)
- **Scenario:** HDBSCAN tags 60%+ of vector embeddings as noise (`cluster = -1`) due to high variance in public user comments.
- **Risk:** Genuine but low-frequency opportunity areas are lost in the noise cluster.
- **Handling Strategy:**
  - Perform hierarchical sub-clustering on the noise cluster (`-1`) with relaxed `min_cluster_size` parameters.

---

## 5. Analytics & Prioritization Edge Cases

### 5.1 Low Sample Size Inflation in Opportunity Scoring
- **Scenario:** A rare blocker mentioned only 2 times, but both instances have an intent score of 1.0 and severity of 3.0.
- **Risk:** High score causes rare edge cases to outrank widely experienced friction points.
- **Handling Strategy:**
  - Apply a minimum frequency threshold ($F \ge F_{min}$, e.g., $F \ge 10$) before an opportunity area is eligible for top-tier ranking in the Opportunity Matrix.

### 5.2 Flash Sale Temporal Distortion
- **Scenario:** During Myntra's End of Reason Sale (EORS), 80%+ of incoming comments discuss price drops and coupon glitches.
- **Risk:** Price sensitivity metrics completely drown out structural Size/Fit and Quality concerns.
- **Handling Strategy:**
  - Provide a **Time-Normalized Trend View** in the dashboard allowing PMs to compare baseline periods vs. sale periods.

---

## 6. Privacy, Security & Compliance Edge Cases

### 6.1 Accidental PII Leaks in Public Comments
- **Scenario:** Users or sellers accidentally post phone numbers, order IDs, delivery addresses, or personal names in Play Store or YouTube comments:
  - *"Myntra order #40928192 for Anita Sharma at Indiranagar was not delivered!"*
- **Risk:** Storing PII in vector payload database violates DPDP Act / GDPR compliance.
- **Handling Strategy:**
  - Enforce a 3-tier PII scrubbing filter (Regex + SpaCy NER + Anonymizer replacement) *before* saving to DuckDB or ChromaDB.

### 6.2 Data Source Availability & Subreddit Deletion
- **Scenario:** A targeted subreddit goes private or Reddit API revokes access token during ingestion.
- **Risk:** Pipeline crashes with unhandled HTTP 403 / 404 errors.
- **Handling Strategy:**
  - Implement graceful fallback degradation: log connector error, notify admin, and proceed with processing remaining active data sources.

---

## Summary Matrix of Edge Case Defenses

| Edge Case Category | Primary Defense Mechanism | Fallback Mechanism |
| :--- | :--- | :--- |
| **Hinglish / Slang** | Hinglish-aware LLM Prompts + Slang Normalizer | Code-mixed translation layer |
| **Sarcasm & Contradiction** | Contradiction analysis with quote justification | Manual inspection flag in Dashboard |
| **Spam / Affiliate Bots** | MinHash / LSH Deduplication + Regex Filter | Author post-rate thresholding |
| **LLM Output Distortion** | Pydantic Schema Validation with Retry Logic | `json_repair` parser fallback |
| **Low Sample Size Inflation** | Minimum frequency filter ($F \ge F_{min}$) | Bayesian smoothed opportunity score |
| **PII Contamination** | Regex + SpaCy NER PII Scrubbing | Zero-PII assertions before write |
