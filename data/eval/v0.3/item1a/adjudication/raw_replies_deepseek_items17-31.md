# DeepSeek raw replies: adjudication items 17-31 (third model family)

- model: DeepSeek web chat (chat.deepseek.com), default model, DeepThink off, web Search turned off (it switched back on in the new chat and was turned off before sending); date 2026-11-16; operated through Claude in Chrome; the chat is kept in the author's DeepSeek history
- attached: item1a_guideline_v2.md and packet_adjudication_items17-31.csv.txt (header + rows 17-31 of packet_adjudication.csv, unchanged)
- prompt: prompt_adjudicator.md with N=15, items 17-31; then "continue"
- replies copied with DeepSeek's own copy button on the CSV block, unchanged
## reply 1 (after the prompt)

item,hunk_id,decision,reason
17,MSFT_FY2026-u059,1,"Only change is 'expanding' to 'evolving' in the law-enforcement data-production sentence, same meaning; labeller 2's ambiguous was unnecessary."
18,MSFT_FY2026-u066,1,"Only change is 'AI services' to 'AI products and services' in an otherwise identical claims/litigation paragraph; boilerplate rewording."
19,MSFT_FY2026-u080,1,"Only change is dropping 'particularly between the U.S. and Europe' from an otherwise identical geopolitical-tension sentence; no substantive change."
20,ORCL_FY2026-u014,1,"Later text is the same acquisitions-risk heading present in the earlier report (match 0.88) with 'joint ventures and strategic alliances' added to the heading; no new risk proposition, so boilerplate rather than material_added."
21,ORCL_FY2026-u022,1,"Later text is the earlier tax-risk paragraph with 'the inability to obtain or retain tax incentives' added to the heading and body; same risk proposition, wording only."
22,ORCL_FY2026-u030,1,"Added sentence is a generic summary of the accounting-estimates risk already disclosed elsewhere in the earlier report; no new risk proposition."
23,ORCL_FY2026-u031,1,"Heading changed from 'Common Stock' to 'Common and Preferred Stock'; no risk proposition changed."
24,ORCL_FY2026-u074,1,"Bullet shortened to 'business disruption and management distraction' — the acquisition/transition/integration qualifier is dropped; slight scope narrowing, but the underlying risk proposition is unchanged, so boilerplate."
25,ORCL_FY2026-u079,1,"Same cybersecurity risk; only rewording (heading rephrased, 'attempts ... to' to 'attacks ... designed to', sentence reordered) with no substantive change."
26,ORCL_FY2026-u085,2,"Earlier tax-audit/liability paragraph is absent from the later report except for a rewritten, broadened tax-law-change paragraph; the specific audit-disagreement and liability risk is no longer disclosed, so material_removed."

## reply 2 (after 'continue')

item,hunk_id,decision,reason
27,ORCL_FY2026-u086,1,"Earlier paragraph on U.S. tax-law changes is gone; later report has a broader OECD/15% minimum-tax paragraph in its place, so the specific risk content was removed or substantively replaced — material_removed is the closer label."
28,ORCL_FY2026-u095,2,"New bullet adds losses from bank failures, fraud, theft, employee misconduct, and payment errors — a risk proposition not stated in the earlier report's cash/liquidity discussion, so material_added."
29,ORCL_FY2026-u099,2,"New healthcare Anti-Kickback Statute/FCA paragraph is a risk proposition (healthcare fraud-and-abuse liability) not disclosed anywhere in the earlier report, so material_added."
30,ORCL_FY2026-u115,1,"Heading broadened to 'Common and Preferred Stock' and new litigation sentence added, but the stock-price risk proposition itself is the same; heading/format change only, boilerplate."
31,ORCL_FY2026-u123,1,"Only change is 'current wars' to 'current wars and conflicts' in an otherwise identical macroeconomic paragraph; same meaning, boilerplate."
