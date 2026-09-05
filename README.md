# AI Risk Manager — Pitch Ready

Defense-only merchant fraud risk workbench.

## Included
- Executive dashboard
- Live transaction risk scoring
- Explainable reason codes
- Transaction queue
- Browser-trained logistic classifier
- 80/20 held-out evaluation
- Precision / recall / F1 / false-positive rate
- Confusion matrix
- Cost-aware threshold optimizer
- Session audit trail
- Demo scenarios for a 5-minute pitch

## Deploy to Vercel
1. Create a public GitHub repository.
2. Upload `index.html` and `vercel.json` to the repository root.
3. Import the repository into Vercel.
4. Leave build command and output directory empty/default.
5. Deploy.
x
## IMPORTANT
The model is trained on synthetic development data generated in the browser. Its metrics are real measurements for that synthetic held-out set, but they are NOT real-world fraud performance.

Before final submission, replace the synthetic benchmark with an allowed public/permitted test-mode dataset and keep the test set untouched during model fitting. Replace illustrative FP/FN costs with merchant-approved assumptions before making business-loss claims.

## Suggested final architecture
Browser UI → validated backend/model service → database/audit store → payment test-mode webhook.

## Defense-only
No fraud-generation, evasion, bypass, or offensive capability is included.
