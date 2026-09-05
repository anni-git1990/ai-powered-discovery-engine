# Context: AI-Powered Discovery Engine for Myntra Wishlist-to-Purchase Behavior

## 1. Project Overview

- **Project Title:** AI-Powered Discovery Engine for Myntra Wishlist-to-Purchase Behavior
- **Domain:** E-Commerce / Fashion Discovery / User Behavior Analysis
- **Target Platform:** Myntra
- **Core Objective:** Build an AI-driven discovery engine to analyze public user conversations and understand what prevents users from converting wishlisted fashion items into completed purchases.

---

## 2. Background & Problem Context

### Background
Myntra users frequently add fashion products to their wishlist while browsing. However, an "Add to Wishlist" action does not reliably translate into a completed purchase. Users add items to their wishlist for diverse reasons, such as:
- Genuine intention to purchase in the near future.
- Saving items to compare options later.
- Waiting for discounts, price drops, or promotional events.
- Hesitation or uncertainty regarding size, fit, quality, or styling.
- Seeking opinions or social validation from friends, family, or online communities.
- Utilizing the wishlist purely as a low-intent bookmarking tool.

### Core Problem
For Myntra, a key product discovery challenge is understanding **what happens between "Add to Wishlist" and "Purchase"**, and identifying the exact barriers delaying or preventing purchase completion.

User feedback addressing these uncertainties is dispersed across vast public channels (e.g., App Store / Play Store reviews, Reddit, YouTube comments, Instagram/social media, fashion forums, Q&A platforms). Manually synthesizing this unstructured qualitative data at scale is impractical.

---

## 3. Key Discovery Questions

The AI Discovery Engine is expected to analyze public user feedback to answer the following questions:

1. **Wishlist Motivation & Intent:**
   - Why do users add products to their Myntra wishlist?
   - How can we distinguish between genuine purchase intent vs. passive bookmarking?

2. **Purchase Blockers & Delays:**
   - What stops or delays users from purchasing wishlisted items?
   - How significantly do price sensitivity and waiting for discounts influence purchase decisions?
   - How much does uncertainty around size, fit, or material quality lower purchase confidence?
   - How do ratings, reviews, and post-purchase concerns (returns, exchanges, delivery) impact conversion?

3. **User Behavior & External Validation:**
   - How do users evaluate and compare multiple wishlisted products?
   - What styling or occasion-related advice do users seek before buying?
   - What information do users search for *outside* Myntra prior to purchasing?
   - How critical is social validation (influencers, Instagram, YouTube, peer feedback)?

4. **Segmentation & Unmet Needs:**
   - How do these purchase behaviors and hesitation patterns differ across distinct user segments?
   - What recurring unmet needs consistently emerge in user conversations?

---

## 4. Target Users

The primary focus is on Myntra fashion shoppers who demonstrate the following behaviors:
- Frequently wishlist products while browsing.
- Revisit wishlisted items multiple times before making a decision.
- Compare multiple products within or across platforms.
- Postpone buying while awaiting price drops or sales.
- Experience uncertainty around size, fit, quality, styling, or occasion suitability.
- Rely on reviews, user feedback, or external social channels before finalizing purchases.
- Ultimately abandon or significantly delay purchase after showing initial interest.

---

## 5. AI Discovery Objectives & Capabilities

The system should move beyond basic sentiment analysis (positive/negative/neutral) to extract structured, actionable product insights from conversational data:

- **Wishlist Motivation Classification:** Identify underlying reasons for wishlisting.
- **Purchase Intent Scoring/Categorization:** Differentiate high-intent buyers from casual browser/bookmarkers.
- **Blocker Identification:** Categorize friction points (price, size/fit, trust, styling, policy).
- **Uncertainty Mapping:** Highlight exact points of user doubt.
- **Delay Reason Categorization:** Understand temporal purchase postponement reasons.
- **Product Comparison Analysis:** Capture cross-product or cross-platform comparison habits.
- **External Search Tracking:** Identify information sought outside Myntra.
- **User Segmentation:** Group feedback by user personas/segments.
- **Opportunity Area Prioritization:** Highlight top recurring unmet needs and highest-impact pain points.

---

## 6. Research Hypotheses & Themes to Investigate

The AI engine evaluates public user conversations across several potential research themes:

| Theme | Description |
| :--- | :--- |
| **Price Sensitivity & Discounts** | Waiting for price drops, sales events, coupon availability. |
| **Size & Fit Uncertainty** | Fear of ordering incorrect size, inconsistent sizing across brands, lack of fit metrics. |
| **Product Quality & Review Trust** | Discrepancies between images and real items, skepticism towards sponsored reviews. |
| **Styling & Occasion Suitability** | Lack of confidence in how to style an item or whether it suits a specific event. |
| **Comparison Friction** | Difficulty comparing specs, prices, or looks between wishlisted items. |
| **Social Validation** | Need for reassurance from peers, Reddit users, YouTube try-on hauls, or influencers. |
| **Fulfillment & Policy Concerns** | Doubts about delivery timelines, return policies, or exchange hassle. |
| **Bookmarking vs. Intent** | Treating wishlist as an aesthetic mood board vs. an active buying cart. |

---

## 7. Expected AI Workflow Pipeline

```
[ Public User Feedback ]
  (App Reviews / Reddit / YouTube / Social Media / Fashion Forums / Product Reviews)
                           │
                           ▼
[ AI Processing Layer ]
  (GPT / Claude / LLM Agents / NLP Pipelines & Classification Workflows)
                           │
                           ▼
[ Structured Analysis ]
  (Classify Intent, Identify Blockers, Map Uncertainties, Categorize Segments)
                           │
                           ▼
[ Quantification & Insight Generation ]
  (Quantify Pattern Frequency, Rank Opportunity Areas, Prioritize User Problems)
                           │
                           ▼
[ Evidence-Based Product Discovery Output ]
```

---

## 8. Success Criteria & Expected Outcomes

### Success Criteria
The engine successfully delivers when it provides clear empirical evidence on:
1. The most prevalent motivations behind Myntra wishlist additions.
2. The primary friction points blocking wishlist-to-purchase conversion.
3. Criteria distinguishing high-intent wishlist additions from casual bookmarking.
4. Key pre-purchase uncertainties and how they vary across user segments.
5. Quantified frequency and severity of identified user pain points.
6. A ranked list of high-leverage product opportunity areas.

### Expected Outcome
At the conclusion of Part 1 (Discovery Phase), the project will provide **data-driven evidence** answering:
> *"Which user problems between adding a product to the Myntra wishlist and completing a purchase are most frequent, important, and worth solving?"*

This evidence will guide leadership and product teams on which specific user problem to prioritize before designing or proposing any solution.
