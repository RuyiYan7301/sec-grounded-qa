# Item 1A v2 adjudication sheet

Disagreements between Claude and ChatGPT (model reported as "5.6 sol") under protocol v2, raw labels.
Section A (confirm, 12 items) first; section B (retest, 13 items) completes the gold but is not part of any agreement figure.
Adjudicate with `item1a_guideline_v2.md`. Raw label files are not changed; decisions go only into `adjudication_log.csv`.
Reply per item: id, final label (one of the five), one-line reason. Example: `C3 boilerplate - same risk still in later paragraph 137`.

## A. Confirmation sample

### C3 · AVGO_FY2024-u130

| | label | conf | reason |
|---|---|---|---|
| Claude | `boilerplate` | 2 | Removed heading; virtualization-demand risk still stated in later para 137. |
| ChatGPT | `material_removed` | 3 | The demand risk for data center virtualization products is no longer disclosed. |

Position: earlier filing paragraph 158 of 292

**CONTEXT ONLY - paragraph before (unchanged)**

> In addition, we may be obligated to indemnify our current or former directors or employees, or former directors or employees of companies that we have acquired, in connection with such litigation. These liabilities could be substantial and may include, among other things, the cost of defending lawsuits against these individuals, as well as stockholder derivative suits; civil or criminal fines and penalties; legal and other expenses; and expenses associated with the remedial measure, if any, which may be imposed.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> If demand for our data center virtualization products is less than anticipated, our business could be adversely affected.

**LABEL THIS - LATER TEXT (added or changed)**

> (none: text removed)

**CONTEXT ONLY - paragraph after (unchanged)**

> Failure of our software products to manage and secure IT infrastructures and environments could have a material adverse effect on our business.

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.56 | later filing, paragraph 172 of 222
> We utilize a significant amount of IP in our business. If we are unable or fail to protect our IP, our business could be adversely affected.
> >
> > [2] match 0.54 | later filing, paragraph 137 of 222
> The growth of our software business depends on demand for our data center virtualization products, as well as customer acceptance of our products, services and business strategy.
> >
> > [3] match 0.48 | later filing, paragraph 31 of 222
> •If we are unable to protect the significant amount of IP we utilize in our business, our business could be adversely affected.

**Final label:** ____________  **Reason:** ____________

---

### C6 · INTC_FY2025-u146

| | label | conf | reason |
|---|---|---|---|
| Claude | `boilerplate` | 2 | Hazardous-materials laws and supplier compliance merged in from adjacent text; same risk. |
| ChatGPT | `material_modified` | 3 | The scope of regulated hazardous-material activities was expanded. |

Position: earlier filing paragraph 169 of 174; later filing paragraph 153 of 154

**CONTEXT ONLY - paragraph before (unchanged)**

> We are subject to risks associated with environmental, health, safety, and product regulations.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> The design, manufacturing, assembly, and test of our products require the use and purchase of materials and chemicals that are subject to a broad array of environmental, health, and safety laws and regulations. Our operations and those of our suppliers are further governed by regulations prohibiting the use of forced labor (e.g., mining conflict minerals), and restrictions on other materials, as well as laws or regulations governing the operation of our facilities, sale and distribution of our products, and use of our real property. The scope and interpretation of such laws and regulations, including the materials they govern, are complex and continue to evolve. The procedures and processes in place under our compliance program may become onerous or increasingly expensive to maintain and cannot guarantee compliance by employees or third parties to whom such laws apply. The amendment or expansion of these laws or regulations, as well as our failure or inability to comply with them (including as a result of acquired entities), can result in regulatory penalties, fines, and legal liabilities; increased costs; additional remediation obligations; suspension of production; alteration, suspension, or termination of our manufacturing and assembly and test processes, including due to an inability to find, afford, or attain adequate substitute materials, equipment, or processes; damage to our reputation; and restrictions on our operations or sales. In addition, the failure or inability to comply by our suppliers of these materials can require us to suspend or alter our production processes and sources, and result in increased risks and costs.

**LABEL THIS - LATER TEXT (added or changed)**

> The design, manufacturing, assembly and test of our products require the use and purchase of materials and chemicals that are subject to a broad array of environmental, health and safety laws and regulations. Our operations and those of our suppliers are further governed by laws and regulations governing the use, transportation, emissions, discharge, storage, recycling or disposal of hazardous materials, prohibiting the use of forced labor (e.g., mining conflict minerals), and placing restrictions on other materials, as well as laws or regulations governing the operation of our facilities, sale and distribution of our products and use of our real property. The scope and interpretation of such laws and regulations, including the materials they govern, are complex and continue to evolve. The procedures and processes in place under our compliance program may become onerous or increasingly expensive to maintain and cannot guarantee compliance by employees or third parties to whom such laws apply. The amendment or expansion of these laws or regulations, as well as the failure or inability of us or our suppliers to comply with them (including as a result of acquired entities), can result in regulatory penalties, fines and legal liabilities; increased costs; additional remediation obligations; suspension of production; alteration, suspension or termination of our manufacturing and assembly and test processes, including due to an inability to find, afford or attain adequate substitute materials, equipment or processes; damage to our reputation; and restrictions on our operations or sales.

**CONTEXT ONLY - paragraph after (unchanged)**

> For example, environmental regulations, including with respect to the materials and processes we are permitted to use and as to air quality and wastewater requirements, may impede our ability to manufacture products or expand or modify our manufacturing capability in the future. Environmental laws and regulations sometimes require us to acquire additional pollution abatement or remediation equipment, modify product designs, cease the use of a particular material or process, remove or remediate hazardous substances or incur other expenses or liabilities. Semiconductor manufacturing uses perfluorocarbons, which have historically made up a large portion of our direct greenhouse gas emissions. New or increased regulations limiting the use of such compounds, or other greenhouse gas emissions, could require us to install additional abatement equipment, purchase carbon offsets and/or alter, where feasible, our production processes and sources. New or more stringent climate change regulations could increase our manufacturing costs associated with meeting air pollution requirements and our energy costs, for example as a result of carbon pricing impacts on electrical utilities. In addition, regulations in response to human health concerns may also limit or prohibit the use of a class of chemicals known as per- and polyfluoroalkyl substances (PFAS), which are found in parts, components, process chemicals and other materials used in semiconductor manufacturing. Such chemicals are critical to the manufacturing and functioning of many semiconductor products and there are limited technically and commercially feasible alternatives. As we expand our manufacturing capacity, the impacts of future laws and regulation could be magnified. Many new materials that we are evaluating for use in our operations are also subject to regulation under environmental laws. These restrictions could harm our business and results of operations by increasing our expenses or requiring us to alter manufacturing and assembly and test processes.

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.37 | later filing, paragraph 154 of 154
> For example, environmental regulations, including with respect to the materials and processes we are permitted to use and as to air quality and wastewater requirements, may impede our ability to manufacture products or expand or modify our manufacturing capability in the future. Environmental laws and regulations sometimes require us to acquire additional pollution abatement or remediation equipment, modify product designs, cease the use of a particular material or process, remove or remediate hazardous substances or incur other expenses or liabilities. Semiconductor manufacturing uses perfluorocarbons, which have historically made up a large portion of our direct greenhouse gas emissions. New or increased regulations limiting the use of such compounds, or other greenhouse gas emissions, could require us to install additional abatement equipment, purchase carbon offsets and/or alter, where feasible, our production processes and sources. New or more stringent climate change regulations could increase our manufacturing costs associated with meeting air pollution requirements and our energy costs, for example as a result of carbon pricing impacts on electrical utilities. In addition, regulations in response to human health concerns may also limit or prohibit the use of a class of chemicals known as per- and polyfluoroalkyl substances (PFAS), which are found in parts, components, process chemicals and other materials used in semiconductor manufacturing. Such chemicals are critical to the manufacturing and functioning of many semiconductor products and there are limited technically and commercially feasible alternatives. As we expand our manufacturing capacity, the impacts of future laws and regulation could be magnified. Many new materials that we are evaluating for use in our operations are also subject to regulation under environmental laws. These restrictions could harm our business and results of operations by increasing our expenses or requiring us to alter manufacturing and assembly and test processes.
> >
> > [2] match 0.33 | later filing, paragraph 9 of 154
> To compete successfully, we must maintain an effective R&D program, develop new products and manufacturing processes, improve our products and processes and make significant capital investments in new and existing manufacturing facilities, all ahead of competitors and market demand. The R&D efforts and capital investments we require are significant as we compete across both product and process technologies and we may not have the ability to fund such investments at the level needed to be competitive. We incurred R&D expenses of $13.8 billion in 2025, $16.5 billion in 2024 and $16.0 billion in 2023. We are focusing our R&D efforts across several key areas, including process and packaging technology, our xPU products and features, AI and software. Our investments are typically long-term and, even where successful, often do not contribute to our operating results for a number of years. We cannot guarantee that our efforts will deliver the benefits we anticipate, including as a result of our new products or technologies falling short of expectations or the offerings of competitors. In recent years, we have had a number of delays in the release of new products, including as a result of defects or errata, late changes to features due to customer requests, or other design challenges for our products. We have similarly had delays in our development of new process technologies and advanced packaging techniques, including with respect to performance and yield. These delays have allowed competitors using third-party foundries, such as TSMC, to benefit from advancements in manufacturing processes introduced ahead of us, including improvements in performance, energy efficiency and other features, which have helped increase the competitiveness of their products. We also missed the significant shift in compute demand to GPUs optimized for AI workloads and have been unsuccessful to date in becoming a meaningful participant in that market while certain of our key competitors have been highly successful in that market. Our most recent efforts to compete in the accelerator market with our Gaudi AI accelerators was unsuccessful, as a result of which we recognized Gaudi AI accelerator inventory-related charges of $375 million in 2025 and $922 million in 2024. To the extent we do not timely introduce new products and manufacturing process technologies that improve performance, performance per watt, transistor density, die utilization, core counts and/or new features such as optimizations for AI and other workloads, with sufficient manufacturing yields and operational efficiency, relative to competitors and competing foundry processes, we have faced and will face cost, product performance and time-to-market disadvantages relative to our competitors. This has in the past and may in the future result in higher operating costs, including as a result of additional costs from unused manufacturing capacity, higher leverage and borrowing costs and pressure on our credit ratings.
> >
> > [3] match 0.33 | later filing, paragraph 51 of 154
> Trade policies and disputes at times result in increased tariffs, trade barriers and other trade restrictions and protectionist measures, which can increase our manufacturing costs, make our products less competitive, reduce demand for our products, limit our ability to sell to certain customers, limit our ability to procure components or raw materials, or impede or slow the movement of our goods across borders. Increasing protectionism and economic nationalism may lead to further changes in trade policies and regulations, domestic sourcing initiatives, or other formal and informal measures that could make it more difficult to sell our products in, or restrict our access to, some markets. They can also result in declining consumer confidence and slowing economic growth or recession, and could cause our customers to reduce, cancel or alter the timing of their purchases with us. Sustained geopolitical tensions could lead to long-term changes in global trade and technology supply chains, domestic sourcing initiatives, and decoupling of global trade networks, which could make it more difficult to sell our products in, or restrict our access to, some markets and have a material adverse effect on our business and growth prospects.

**CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3)**

> [1] match 0.38 | earlier filing, paragraph 170 of 174
> The failure or inability by us, our customers, or our suppliers to manage the use, transportation, emissions, discharge, storage, recycling, or disposal of hazardous materials can lead to increased costs or future liabilities. Environmental regulations, including with respect to the materials and processes we are permitted to use and as to air quality and wastewater requirements, may impede our ability to manufacture products or expand or modify our manufacturing capability in the future. Environmental laws and regulations sometimes require us to acquire additional pollution abatement or remediation equipment, modify product designs, cease the use of a particular material or process, remove or remediate hazardous substances, or incur other expenses or liabilities. Regulations in response to climate change could result in increased manufacturing costs associated with air pollution requirements. For example, semiconductor manufacturing uses perfluorocarbons, which have historically made up a large portion of our direct greenhouse gas emissions. New or increased regulations limiting the use of such compounds, or other greenhouse gas emissions, could require us to install additional abatement equipment, purchase carbon offsets, and/or alter, where feasible, our production processes and sources. In addition, new or increased climate change regulation could increase our energy costs, for example as a result of carbon pricing impacts on electrical utilities. Regulations in response to human health concerns may also limit or prohibit the use of a class of chemicals known as per- and polyfluoroalkyl substances (PFAS), which are found in parts, components, process chemicals, and other materials used in semiconductor manufacturing. Such chemicals are critical to the manufacturing and functioning of many semiconductor products and there are limited
> >
> > [2] match 0.35 | earlier filing, paragraph 142 of 174
> We face risks related to transactions with government entities. We receive proceeds from both US and non-US governments associated with grants, incentives, and sales of our products and services, and we are seeking to increase our sales of products and services to governmental entities in the future. Government demand and payment are often affected by public sector budgetary cycles and funding authorizations, including, with respect to US government contracts, congressional approval of appropriations, and can be adversely impacted by shutdowns of the US federal government and changes in US administration, including administrative priorities. Government contracts are subject to procurement laws and regulations relating to the award, administration, and performance of those contracts, as well as oversight and penalties for violations. For example, certain agreements with the US government are subject to special rules on accounting, IP rights, expenses, reviews, information handling, security, customers, and/or employees, and failure or inability to comply with these rules could result in civil and criminal penalties and sanctions, including termination of contracts, fines, and suspension or debarment from future business with the US government.
> >
> > [3] match 0.34 | earlier filing, paragraph 149 of 174
> Our policies, controls, and procedures designed to help provide for compliance with applicable laws cannot provide assurance that our employees, contractors, suppliers, or agents will not violate such laws or our policies. Violations of these laws and regulations can result in fines; criminal sanctions against us, our officers, or our employees; prohibitions on the conduct of our business; and damage to our reputation. The technology industry is subject to intense media, political, and regulatory scrutiny, which can increase our exposure to government investigations, legal actions, and penalties.

**Final label:** ____________  **Reason:** ____________

---

### C10 · AVGO_FY2024-u198

| | label | conf | reason |
|---|---|---|---|
| Claude | `ambiguous` | 1 | FX remeasurement explanation removed while FX heading stays; unclear whether the risk is still described. |
| ChatGPT | `material_removed` | 3 | The foreign-exchange exposure risk is no longer disclosed. |

Position: earlier filing paragraph 233 of 292

**CONTEXT ONLY - paragraph before (unchanged)**

> Fluctuations in foreign exchange rates could result in losses.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> We operate global businesses and our consolidated financial results are reported in U.S. dollars. However, some of the revenue and expenses of our foreign subsidiaries are denominated in local currencies. Fluctuations in foreign exchange rates against the U.S. dollar could result in substantial changes in reported revenues and operating results due to the foreign exchange impact of remeasuring these transactions into U.S. dollars.

**LABEL THIS - LATER TEXT (added or changed)**

> (none: text removed)

**CONTEXT ONLY - paragraph after (unchanged)**

> We have potential tax liabilities as a result of VMware's former controlling ownership by Dell, which could have an adverse effect on our financial condition and operating results.

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.37 | later filing, paragraph 136 of 222
> A successful cyber-attack involving our products could cause customers and potential customers to believe our services are ineffective or unreliable and result in, among other things, the loss of customers, unfavorable publicity, damage to our reputation, difficulty in marketing our products, and allegations by our customers that we have not performed our contractual obligations, and give rise to significant costs, including costs related to developing solutions or indemnification obligations under our agreements. Any such event could adversely impact our revenue and results of operations. See also "Cyber security threats or other security breaches, or any other impairment of the confidentiality, integrity or availability of our IT systems, or those of one or more of our corporate infrastructure vendors, could have a material adverse effect on our business."
> >
> > [2] match 0.36 | later filing, paragraph 165 of 222
> The foregoing factors are often difficult to predict, and these, as well as other factors, could materially adversely affect our quarterly or annual operating results. In addition, a significant amount of our operating expenses are relatively fixed in nature. Any failure to adjust spending quickly enough to compensate for a revenue shortfall could magnify the adverse impact of such revenue shortfall on our results of operations. As a result, we believe that quarter-to-quarter comparisons of our revenue and operating results may not be meaningful or reliable indicators of our future performance. If our operating results in one or more future quarters fail to meet the expectations of securities analysts or investors, a significant decline in the trading price of our common stock may occur, which may happen immediately or over time.
> >
> > [3] match 0.36 | later filing, paragraph 113 of 222
> Our manufacturing processes and those of our CMs rely on many materials, including silicon, GaAs and InP wafers, copper lead frames, precious and rare earth metals, mold compound, ceramic packages and various chemicals and gases. During fiscal year 2024, we purchased approximately two-thirds of our manufacturing materials from five materials suppliers, some of which are single source suppliers. The lead time needed to identify and qualify a new supplier is typically lengthy and there is often no readily available alternative source. We do not generally have long-term contracts with our materials suppliers and substantially all of our purchases are on a purchase order basis. Suppliers may extend lead times, limit supplies, place products on allocation or increase prices, any of which could disrupt supply or increase demand in the industry. Additionally, the supply of these materials may be negatively impacted by increased trade tensions between the U.S. and its trading partners, particularly China. Any such supply constraints could result in loss of revenue opportunities and adversely impact our business, financial condition and results of operations.

**Final label:** ____________  **Reason:** ____________

---

### C13 · INTC_FY2025-u070

| | label | conf | reason |
|---|---|---|---|
| Claude | `material_added` | 2 | New risk of competitive disadvantage from not adopting AI in operations; no earlier match. |
| ChatGPT | `material_modified` | 3 | The later text adds competitive disadvantage from failing to adopt AI as effectively as competitors. |

Position: earlier filing paragraph 65 of 174; later filing paragraph 70 of 154

**CONTEXT ONLY - paragraph before (unchanged)**

> Risk Factors and Other Key Information expect to continue to make to develop products and software to address what we believe will be increasing demand for AI capabilities, most notably in AI PCs but also in the data center and in GPUs, may be insufficient, and we face significant hurdles, including whether demand will materialize, whether third-party developers will develop the software to utilize the AI capabilities of our products, and whether we will be successful in developing products that can compete with offerings by established competitors.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> Our use of AI technology may subject us to reputational, financial, legal, or regulatory risks. As we incorporate AI technology into our products and services, any failure to address concerns relating to the responsible use of the evolving AI technology in our products and services may cause harm to our reputation or financial liability and, as such, may increase our costs to address or mitigate such risks and issues. AI technology may create ethical issues, generate defective algorithms, and present other risks that create challenges with respect to its adoption. In addition, evolving laws, rules, regulations, and industry standards governing AI may require us to expend significant resources to modify, maintain, or align our business practices or products.

**LABEL THIS - LATER TEXT (added or changed)**

> Our use of AI technology may subject us to reputational, financial, legal or regulatory risks. As we incorporate AI technology into our products and services, any failure to address concerns relating to the responsible use of the evolving AI technology in our products and services may cause harm to our reputation or financial liability and, as such, may increase our costs to address or mitigate such risks and issues. AI technology may create ethical issues, generate defective algorithms and present other risks that create challenges with respect to its adoption. In addition, evolving laws, rules, regulations and industry standards governing AI may require us to expend significant resources to modify, maintain or align our business practices or products. At the same time, to the extent we do not adopt AI technology in the operation of our business as effectively as our competitors, we may be competitively disadvantaged.

**CONTEXT ONLY - paragraph after (unchanged)**

> We rely upon a complex global supply chain.

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.36 | later filing, paragraph 128 of 154
> We face risks related to sales through distributors and other third parties. We sell a significant portion of our products through third parties, such as distributors, value-added resellers and channel partners (collectively referred to as distributors), as well as OEMs and ODMs. We depend on many distributors to help us create end-customer demand, provide technical support and other value-added services to customers, fill customer orders and stock our products. At times, we rely on one or more key distributors for a product, and a material change in our relationship with one or more of these distributors or their failure to perform as expected could reduce our revenue. Our ability to add or replace distributors for some of our products is limited. In addition, our distributors' expertise in the determination and stocking of acceptable inventory levels for some of our products is not always easily transferable to a new distributor; as a result, end customers may be hesitant to accept the addition or replacement of a distributor. Using third parties for distribution exposes us to many risks, including competitive pressure and concentration, credit and compliance risks. Distributors and other third parties often sell products that compete with our products, and we sometimes need to provide financial and other incentives to focus them on the sale of our products. From time to time, they may face financial difficulties, including bankruptcy, which could harm our collection of accounts receivable and financial results. Further, any violations of the Foreign Corrupt Practices Act or similar laws by distributors or other third-party intermediaries could have a material impact on our business, including subjecting us to litigation or regulatory risk. In addition, to the extent we are not able to keep our products away from the "gray market," demand and pricing dynamics can become distorted in our distribution channel and certain geographies, adversely affecting our revenue. Failure to manage risks related to our use of distributors and other third parties may reduce sales, increase expenses and weaken our competitive position.
> >
> > [2] match 0.36 | later filing, paragraph 90 of 154
> These costs could be large and may increase expenses and lower gross margin, and/or result in delay or loss of revenue. Mitigation techniques designed to address product issues, including software and firmware updates, are not always available on a timely basis—or at all—and do not always operate as intended or effectively resolve such issues for all applications. We and third parties, such as hardware and software vendors, make prioritization decisions about which product issues to address, which can delay, limit or prevent development or deployment of a mitigation and harm our reputation and result in costs. Product defects, errata or other product issues and/or mitigation techniques can result in product failures, adverse performance and power effects, reboots, system instability or unavailability, loss of functionality, data loss or corruption, unpredictable system behavior, decisions by customers and end users to limit or change the applications in which they use our products or product features and other issues. For example, during 2024, some of our customers experienced instability issues when using Intel Core 13th and 14th Gen desktop processors, which required us to undertake an investigation and deploy corrective actions. This adversely impacted sales volume during 2024 and may result in higher warranty costs in the future.
> >
> > [3] match 0.36 | later filing, paragraph 134 of 154
> We are subject to complex and evolving laws and regulations worldwide that differ among jurisdictions and affect our operations in areas including, but not limited to: IP ownership and infringement; tax; import and export requirements; anti-corruption; foreign exchange controls and cash repatriation restrictions; data privacy and localization requirements; competition; advertising; employment and labor; product regulations; environment, health and safety requirements; and consumer laws. Compliance with such requirements can be onerous and expensive and may otherwise impact our business operations negatively. Expanding privacy legislation and compliance costs of privacy-related and data-protection measures could adversely affect our customers and their products and services, particularly in cloud, Internet of Things and AI applications, which could in turn reduce demand for our products used for those workloads. Our policies, controls and procedures designed to help provide for compliance with applicable laws cannot provide assurance that our employees, contractors, suppliers or agents will not violate such laws or our policies. Violations of these laws and regulations can result in fines; criminal sanctions against us, our officers or our employees; prohibitions on the conduct of our business; and damage to our reputation.

**CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3)**

> [1] match 0.37 | earlier filing, paragraph 92 of 174
> Security vulnerabilities and any limitations or adverse effects of mitigation techniques can adversely affect our results of operations, financial condition, customer relationships, prospects, and reputation in a number of ways, any of which may be material. For example, whether or not vulnerabilities involve attempted or successful exploits, they may result in our incurring significant costs related to developing and deploying updates and mitigations, writing down inventory value, defending against product claims and litigation, responding to regulatory inquiries or actions, paying damages, addressing customer satisfaction considerations, providing product replacements or modifications, or taking other remedial steps with respect to third parties. Adverse publicity about security vulnerabilities or mitigations could damage our reputation with customers or users and reduce demand for our products and services. These effects may be greater to the extent that competing products are not susceptible to the same vulnerabilities or if vulnerabilities can be more effectively mitigated in competing products. Moreover, third parties can release information regarding potential vulnerabilities of our products before mitigations are available, which, in turn, could lead to attempted or successful exploits, adversely affect our ability to introduce mitigations, or otherwise harm our business and reputation.
> >
> > [2] match 0.36 | earlier filing, paragraph 148 of 174
> We are subject to complex and evolving laws and regulations worldwide that differ among jurisdictions and affect our operations in areas including, but not limited to: IP ownership and infringement; tax; import and export requirements; anti-corruption; foreign exchange controls and cash repatriation restrictions; data privacy and localization requirements; competition; advertising; employment and labor; product regulations; environment, health, and safety requirements; and consumer laws. Compliance with such requirements can be onerous and expensive and may otherwise impact our business operations negatively. For example, unfavorable developments with evolving laws and regulations worldwide related to 5G or autonomous driving technology and MaaS may limit global adoption, impede our strategy, or negatively impact our long-term expectations for our investments in these areas. Expanding privacy legislation and compliance costs of privacy-related and data-protection measures could adversely affect our customers and their products and services, particularly in cloud, Internet of Things, and AI applications, which could in turn reduce demand for our products used for those workloads.
> >
> > [3] match 0.36 | earlier filing, paragraph 136 of 174
> We face risks related to sales through distributors and other third parties. We sell a significant portion of our products through third parties, such as distributors, value-added resellers, and channel partners (collectively referred to as distributors), as well as OEMs and ODMs. We depend on many distributors to help us create end-customer demand, provide technical support and other value-added services to customers, fill customer orders, and stock our products. At times, we rely on one or more key distributors for a product, and a material change in our relationship with one or more of these distributors or their failure to perform as expected could reduce our revenue. Our ability to add or replace distributors for some of our products is limited. In addition, our distributors' expertise in the determination and stocking of acceptable inventory levels for some of our products is not always easily transferable to a new distributor; as a result, end customers may be hesitant to accept the addition or replacement of a distributor. Using third parties for distribution exposes us to many risks, including competitive pressure and concentration, credit, and compliance risks. Distributors and other third parties often sell products that compete with our products, and we sometimes need to provide financial and other incentives to focus them on the sale of our products. From time to time, they may face financial difficulties, including bankruptcy, which could harm our collection of accounts receivable and financial results. Further, any violations of the Foreign Corrupt Practices Act or similar laws by distributors or other third-party intermediaries could have a material impact on our business, including subjecting us to litigation or regulatory risk. Failure to manage risks related to our use of distributors and other third parties may reduce sales, increase expenses, and weaken our competitive position.

**Final label:** ____________  **Reason:** ____________

---

### C16 · AVGO_FY2024-u116

| | label | conf | reason |
|---|---|---|---|
| Claude | `material_modified` | 2 | Statement that extended lead times have limited and may limit order fulfillment dropped; general demand-response risk kept. |
| ChatGPT | `material_removed` | 3 | Specific risks from build-to-order production, extended lead times, and rapid demand increases are no longer disclosed. |

Position: earlier filing paragraph 135 of 292

**CONTEXT ONLY - paragraph before (unchanged)**

> We make significant decisions, including determining the levels of business that we will seek and accept, production schedules, levels of reliance on contract manufacturing and outsourcing, internal fabrication utilization and other resource requirements, based on customer requirements or estimates thereof, which may not be accurate.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> We largely build to order and have extended customer lead times substantially, which has limited and may continue to limit our ability to fulfill orders and satisfy all of the demand for our products. Customers may require rapid increases in production on short notice. If we are unable to meet such increases in demand, this could damage our customer relationships, reduce revenue growth and margins, subject us to additional liabilities, harm our reputation, and prevent us from taking advantage of opportunities.

**LABEL THIS - LATER TEXT (added or changed)**

> (none: text removed)

**CONTEXT ONLY - paragraph after (unchanged)**

> We may be unable to maintain appropriate manufacturing capacity or product yields at our own manufacturing facilities, which could adversely affect our relationships with our customers, and our business, financial condition and results of operations.

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.46 | later filing, paragraph 118 of 222
> We make significant decisions, including determining the levels of business that we will seek and accept, production schedules, levels of reliance on contract manufacturing and outsourcing, internal fabrication utilization and other resource requirements, based on customer requirements or estimates thereof, which may not be accurate. Many factors could impact our estimates of customers' demands, including changes in product development cycles, competing technologies and product releases, new or unexpected end-user products, such as demand for AI-related products, and changes in business and economic conditions. If we are unable to timely respond to changes in customer demand, this could damage our customer relationships, harm our reputation, prevent us from taking advantage of opportunities and adversely impact our business, financial condition and results of operations.
> >
> > [2] match 0.39 | later filing, paragraph 185 of 222
> In addition, an increasing number of OEMs are seeking to source products that do not contain conflict minerals. This could adversely affect the sourcing, availability and pricing of minerals used in the manufacture of semiconductor devices, including our products. As a result, we may face difficulties in satisfying our customers' demands, which may harm our sales and operating results.
> >
> > [3] match 0.37 | later filing, paragraph 116 of 222
> A prolonged disruption at or shut-down of one or more of our manufacturing facilities or warehouses or those of our CMs or suppliers, due to natural- or man-made disasters or other events outside of our control, such as climate change, water shortages, political unrest, military conflicts, geopolitical turmoil, trade tensions, government orders, labor shortages, medical epidemics, economic instability, equipment failure or for any other reason, would limit our capacity to meet customer demands and delay new product development until a replacement facility and equipment, if necessary, were found. To date, such events have not had a material adverse effect on our business. However, such an event could disrupt our operations, forgo revenue opportunities, potentially lose market share, result in us being unable to timely satisfy customer demand, expose us to claims by our customers, result in significant expense to repair or replace our affected facilities, and, in some instances, could significantly curtail our research and development efforts in a particular product area or target market, any of which could materially and adversely affect our business. This disruption could also prevent our customers from resuming their own manufacturing following such an event, they may cancel or scale back their orders from us and this may in turn adversely affect our results of operations. Such events could also result in increased fixed costs relative to the revenue we generate and adversely affect our results of operations.

**Final label:** ____________  **Reason:** ____________

---

### C26 · AVGO_FY2024-u115

| | label | conf | reason |
|---|---|---|---|
| Claude | `material_modified` | 2 | Adds new demand-estimation factors (incl. AI-related product demand) and consequences to the same risk. |
| ChatGPT | `material_added` | 3 | The later filing adds risks from inaccurate demand estimates and inability to respond timely to customer demand. |

Position: earlier filing paragraph 134 of 292; later filing paragraph 118 of 222

**CONTEXT ONLY - paragraph before (unchanged)**

> Failure to adjust our manufacturing and supply chain to accurately meet customer demand could adversely affect our results of operations.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> We make significant decisions, including determining the levels of business that we will seek and accept, production schedules, levels of reliance on contract manufacturing and outsourcing, internal fabrication utilization and other resource requirements, based on customer requirements or estimates thereof, which may not be accurate.

**LABEL THIS - LATER TEXT (added or changed)**

> We make significant decisions, including determining the levels of business that we will seek and accept, production schedules, levels of reliance on contract manufacturing and outsourcing, internal fabrication utilization and other resource requirements, based on customer requirements or estimates thereof, which may not be accurate. Many factors could impact our estimates of customers' demands, including changes in product development cycles, competing technologies and product releases, new or unexpected end-user products, such as demand for AI-related products, and changes in business and economic conditions. If we are unable to timely respond to changes in customer demand, this could damage our customer relationships, harm our reputation, prevent us from taking advantage of opportunities and adversely impact our business, financial condition and results of operations.

**CONTEXT ONLY - paragraph after (unchanged)**

> We may be unable to maintain appropriate manufacturing capacity or product yields at our own manufacturing facilities, which could adversely affect our relationships with our customers, and our business, financial condition and results of operations.

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.39 | later filing, paragraph 191 of 222
> Significant judgment is required in determining our worldwide income taxes, and our calculations of income taxes payable currently and on a deferred basis are based on our interpretations of applicable tax laws. Although we believe our tax estimates are reasonable, there is no assurance that the final determination of our income tax liability will not be materially different than what is reflected in our income tax provisions and accruals. In addition, we are subject to, and are under, tax audits in various jurisdictions. Although we believe our tax positions are reasonable, the final determination of tax audits could be materially different from our income tax provisions and accruals, which could have a material adverse effect on our results of operations and cash flows in the period or periods for which that determination is made.
> >
> > [2] match 0.36 | later filing, paragraph 74 of 222
> •difficulties integrating the acquired business or company and in managing and retaining acquired employees, vendors and customers; and
> >
> > [3] match 0.35 | later filing, paragraph 62 of 222
> A significant legal risk associated with conducting business internationally is compliance with the various and differing laws and regulations of the many countries in which we do business. Although our policies prohibit us, our employees and our agents from engaging in unethical business practices, there can be no assurance that all of our employees, distributors or other agents will refrain from acting in violation of our related anti-corruption or other policies and procedures. Any such violation could have a material adverse effect on our business.

**CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3)**

> [1] match 0.39 | earlier filing, paragraph 139 of 292
> Winning a product design does not guarantee sales to a customer. A delay or cancellation of a customer's plans could materially and adversely affect our financial results, as we incur significant expense in the design process and may generate little or no revenue from it. In addition, the timing of design wins is unpredictable and implementing production for a major design win, or multiple design wins at the same time, may strain our resources and those of our CMs. In such event, we may be forced to dedicate significant additional resources and incur additional costs and expenses. Further, often customers will only purchase limited numbers of evaluation units until they qualify the products and/or the manufacturing line for those products. The qualification process can take significant time and resources. Delays in qualification or failure to qualify our products may cause a customer to discontinue use of our products and result in a significant loss of revenue. Finally, customers could choose at any time to stop using our products or could fail to successfully market and sell their products, which could reduce demand for our products and cause us to hold excess inventory, materially adversely affecting our business, financial condition and results of operations. These risks are exacerbated by the fact that many of our products, and the end products into which our products are incorporated, often have very short life cycles.
> >
> > [2] match 0.39 | earlier filing, paragraph 132 of 292
> Our manufacturing processes and those of our CMs rely on many materials, including silicon, GaAs and InP wafers, copper lead frames, precious and rare earth metals, mold compound, ceramic packages and various chemicals and gases. During fiscal year 2023, we purchased approximately two-thirds of our manufacturing materials from five materials providers, some of which are single source suppliers. As certain materials are highly specialized, the lead time needed to identify and qualify a new supplier is typically lengthy and there is often no readily available alternative source. We do not generally have long-term contracts with our materials providers and substantially all of our purchases are on a purchase order basis. Suppliers may extend lead times, limit supplies, place products on allocation or increase prices due to commodity price increases, capacity constraints, inflation, or other factors, any of which could lead to interruption of supply or increased demand in the industry. For example, macroeconomic and geopolitical conditions, as well as the COVID-19 pandemic, caused some supply constraints and increases in prices, including with respect to wafers and substrates. Additionally, the supply of these materials may be negatively impacted by increased trade tensions between the U.S. and its trading partners, particularly China. Any such supply constraints could result in loss of revenue opportunities and adversely impact our business, financial condition and results of operations.
> >
> > [3] match 0.39 | earlier filing, paragraph 135 of 292
> We largely build to order and have extended customer lead times substantially, which has limited and may continue to limit our ability to fulfill orders and satisfy all of the demand for our products. Customers may require rapid increases in production on short notice. If we are unable to meet such increases in demand, this could damage our customer relationships, reduce revenue growth and margins, subject us to additional liabilities, harm our reputation, and prevent us from taking advantage of opportunities.

**Final label:** ____________  **Reason:** ____________

---

### C28 · NVDA_FY2025-u027

| | label | conf | reason |
|---|---|---|---|
| Claude | `boilerplate` | 2 | Health-related lockdown factor reworded with same meaning. |
| ChatGPT | `material_modified` | 3 | The later text broadens the risk from government actions controlling disease spread to public health issues generally. |

Position: earlier filing paragraph 54 of 197; later filing paragraph 54 of 209

**CONTEXT ONLY - paragraph before (unchanged)**

> •changes in business and economic conditions resulting in decreased end demand;

**LABEL THIS - EARLIER TEXT (removed or changed)**

> •sudden or sustained government lockdowns or actions to control case spread of global or local health issues;

**LABEL THIS - LATER TEXT (added or changed)**

> •sudden or sustained government lockdowns or public health issues;

**CONTEXT ONLY - paragraph after (unchanged)**

> •rapidly changing technology or customer requirements;

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.47 | later filing, paragraph 65 of 209
> •government actions or changes in governmental policies, such as export controls, increased restrictions on gaming usage, or tariffs; and
> >
> > [2] match 0.40 | later filing, paragraph 185 of 209
> Additionally, restrictions imposed by the Chinese government on the duration of gaming activities and access to games may adversely affect our Gaming revenue, and increased oversight of digital platform companies may adversely affect our Data Center revenue. The Chinese government may also encourage customers to purchase from our China-based competitors, or impose restrictions on the sale to certain customers of our products, or any products containing components made by our partners and suppliers. For example, the Chinese government announced restrictions relating to certain sales of products containing certain products made by Micron, a supplier of ours. As another example, an agency of the Chinese government announced an Action Plan that endorses new standards regarding the compute performance per watt and per memory bandwidth of accelerators used in new and renovated data centers in China. If the Chinese government modifies or implements the Action Plan in a way that effectively prevents us from being able to design products to meet the new standard, this may restrict the ability of customers to use some of our data center products and may have a material and adverse impact on our business, operating results and financial condition. Further restrictions on our products or the products of our suppliers could negatively impact our business and financial results.
> >
> > [3] match 0.40 | later filing, paragraph 199 of 209
> In the ordinary course of business, we transfer personal data from Europe, China, and other jurisdictions to the United States or other countries. Certain jurisdictions have enacted data localization laws and cross-border personal data transfer laws. For example, the GDPR governs the transfer of personal data to countries outside of the EEA. The European Commission released a set of "Standard Contractual Clauses" designed for entities to validly transfer personal data out of the EEA to jurisdictions that the European Commission has not found to provide an adequate level of protection, including the United States. Additionally, the U.K.'s International Data Transfer Agreement / Addendum, as well as the EU-U.S. Data Privacy Framework and the U.K. extension thereto (which allows for transfers to relevant U.S.-based organizations who self-certify compliance and participate in the Framework) are mechanisms that may be used to transfer personal data from the EEA and U.K. to the United States. However, these mechanisms are subject to legal challenges, and there is no assurance that we can satisfy or rely on these measures to lawfully transfer personal data to the United States. Other jurisdictions have enacted or are considering similar cross-border personal data transfer laws and local personal data residency laws, any of which would increase the cost and complexity of doing business and could result in fines from regulators. For example, China's law imposes various requirements relating to data processing and data localization. Data broadly defined as important under China's law, including personal data, may not be transferable outside of China without prior assessment and approval by the Cyberspace Administration of China, or CAC. Compliance with these requirements, including CAC assessments and any deemed failures of such assessments, could cause us to incur liability, prevent us from using data collected in China or impact our ability to transfer data outside of China. The inability to import personal data to the United States could significantly and negatively impact our business operations, limit our ability to collaborate with parties that are subject to European, China and other data privacy and security laws, or require us to increase our personal data processing capabilities in Europe and/or elsewhere at significant expense. Some European regulators have prevented companies from transferring personal data out of Europe for allegedly violating the GDPR's cross-border data transfer limitations, which could negatively impact our business.

**CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3)**

> [1] match 0.40 | earlier filing, paragraph 53 of 197
> •changes in business and economic conditions resulting in decreased end demand;
> >
> > [2] match 0.40 | earlier filing, paragraph 153 of 197
> Any of the factors discussed above could prevent us from achieving our anticipated financial results. For example, we have granted and may continue to grant extended payment terms to some customers, particularly during macroeconomic downturns, which could impact our ability to collect payment. Our vendors have requested and may continue to ask for shorter payment terms, which may impact our cash flow generation. These arrangements reduce the cash we have available for general business operations. In addition, the pace of growth in our operating expenses and investments may lag our revenue growth, creating volatility or periods where profitability levels may not be sustainable. Failure to meet our expectations or the expectations of our investors or security analysts is likely to cause our stock price to decline, as it has in the past, or experience substantial price volatility.
> >
> > [3] match 0.39 | earlier filing, paragraph 151 of 197
> •unanticipated costs associated with environmental liabilities; and

**Final label:** ____________  **Reason:** ____________

---

### C35 · AVGO_FY2024-u171

| | label | conf | reason |
|---|---|---|---|
| Claude | `ambiguous` | 1 | Merges earlier para 212 (present) and adds insufficient-IP-rights clause; dropped list lead-in may mean list items removed, unclear from text. |
| ChatGPT | `material_modified` | 3 | The later text adds risks from insufficient rights, jurisdictional limits, and patent expirations. |

Position: earlier filing paragraph 205 of 292; later filing paragraph 173 of 222

**CONTEXT ONLY - paragraph before (unchanged)**

> We utilize a significant amount of IP in our business. If we are unable or fail to protect our IP, our business could be adversely affected.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> Our success depends in part upon protecting our IP. To accomplish this, we rely on a combination of IP rights, including patents, copyrights, trademarks and trade secrets, as well as customary contractual protections with our customers, suppliers, employees and consultants. We spend significant resources to monitor and protect our IP rights, including the unauthorized use of our products, usage rates of the software seat licenses and subscriptions that we sell, and even with significant expenditures, we may not be able to protect the IP rights that are valuable to our business. We are unable to predict or assure that:

**LABEL THIS - LATER TEXT (added or changed)**

> Our success depends in part upon protecting our IP. To accomplish this, we rely on a combination of IP rights, including patents, copyrights, trademarks and trade secrets, as well as customary contractual protections with our customers, suppliers, employees and consultants. We spend significant resources to monitor and protect our IP rights, including the unauthorized use of our products and usage rates of the software seat licenses and subscriptions that we sell. Even with significant expenditures, we may not be able to protect the IP rights that are valuable to our business or have sufficient IP rights to protect our products or our business. Further, effective IP protection may be unavailable or more limited in other jurisdictions, relative to those protections available in the U.S., and may not be applied for or may be abandoned in one or more relevant jurisdictions. In addition, when patents expire, we lose the protection and competitive advantages they provided to us.

**CONTEXT ONLY - paragraph after (unchanged)**

> We also generate revenue from licensing royalty payments and from technology claim settlements relating to certain of our IP. Licensing of our IP rights, particularly exclusive licenses, may limit our ability to assert those IP rights against third parties, including the licensee of those rights. In addition, from time to time, we acquire companies with IP that is subject to licensing obligations to other third parties. These licensing obligations have extended, and may in the future extend, to our own IP, limiting our ability to assert our IP rights.

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.38 | later filing, paragraph 175 of 222
> From time to time, we pursue litigation to assert our IP rights, including, in some cases, against our customers and suppliers. Claims of this sort could also harm our relationships with our customers and might deter future customers from doing business with us. Conversely, third parties have and may in the future pursue IP litigation against us, including as a result of our IP licensing business. Any inability to adequately protect our IP could limit the value of our technology, result in the loss of opportunities to sell or license our technology to others or limit our collection of royalty payments, any of which could negatively impact our business, financial condition and results of operations.
> >
> > [2] match 0.36 | later filing, paragraph 123 of 222
> The industries in which we operate are characterized by companies holding large numbers of patents, copyrights, trademarks and trade secrets and vigorously pursuing, protecting and enforcing IP rights, including actions by patent-holding companies that do not make or sell products. From time to time, third parties assert against us and our customers and distributors their IP rights to technologies that are important to our business. We may be required to indemnify our customers or purchasers for third-party IP infringement claims, including costs to defend those claims, and payment of damages in the case of adverse rulings. However, our CMs and suppliers may or may not be required to indemnify us should we or our customers be subject to such third-party claims. Claims of this sort could also harm our relationships with our customers and might deter future customers from doing business with us. If any pending or future proceedings result in an adverse outcome, we could be required to:
> >
> > [3] match 0.36 | later filing, paragraph 110 of 222
> TSMC, one of our CMs, manufactured approximately 95% of the wafers manufactured by our CMs during fiscal year 2024. We believe our wafer requirements represent a meaningful portion of TSMC's total production capacity. However, TSMC also fabricates wafers for other companies, including some of our competitors, and could choose or be required to prioritize capacity for other customers or reduce or eliminate deliveries to us on short notice. In addition, TSMC has, and may in the future, raise their prices to us.

**CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3)**

> [1] match 0.53 | earlier filing, paragraph 212 of 292
> Effective IP protection may be unavailable or more limited in other jurisdictions, relative to those protections available in the U.S., and may not be applied for or may be abandoned in one or more relevant jurisdictions. In addition, when patents expire, we lose the protection and competitive advantages they provided to us.
> >
> > [2] match 0.40 | earlier filing, paragraph 213 of 292
> We also generate revenue from licensing royalty payments and from technology claim settlements relating to certain of our IP. Licensing of our IP rights, particularly exclusive licenses, may limit our ability to assert those IP rights against third parties, including the licensee of those rights. In addition, we may acquire companies with IP that is subject to licensing obligations to other third parties. These licensing obligations may extend to our own IP following any such acquisition and may limit our ability to assert our IP rights. From time to time, we pursue litigation to assert our IP rights, including, in some cases, against our customers and suppliers. Claims of this sort could also harm our relationships with our customers and might deter future customers from doing business with us. Conversely, third parties have and may in the future pursue IP litigation against us, including as a result of our IP licensing business. An adverse decision in such types of legal action could limit our ability to assert our IP rights and limit the value of our technology, including the loss of opportunities to sell or license our technology to others or to collect royalty payments, which could otherwise negatively impact our business, financial condition and results of operations.
> >
> > [3] match 0.37 | earlier filing, paragraph 217 of 292
> Product liability insurance is subject to significant deductibles and there is no guarantee that such insurance will be available or adequate to protect against all such claims, or we may elect to self-insure with respect to certain matters. For example, it is possible for one of our customers to recall a product containing one of our semiconductor devices. In such an event, we may incur significant costs and expenses, including among others, replacement costs, contract damage claims from our customers and reputational harm. Although we maintain reserves for reasonably estimable liabilities and purchase product liability insurance, our reserves may be inadequate to cover the uninsured portion of such claims. Conversely, in some cases, amounts we reserve may ultimately exceed our actual liability for particular claims and may need to be reversed.

**Final label:** ____________  **Reason:** ____________

---

### C37 · NVDA_FY2025-u041

| | label | conf | reason |
|---|---|---|---|
| Claude | `material_modified` | 2 | Condensed into later para 49 but past amplification (were amplified) became hypothetical (would be amplified). |
| ChatGPT | `boilerplate` | 3 | The same demand, inventory, pricing, and purchase-commitment risks remain disclosed with wording changes. |

Position: earlier filing paragraph 69 of 197

**CONTEXT ONLY - paragraph before (unchanged)**

> If we underestimate our customers' future demand for our products, our foundry partners may not have adequate lead-time or capacity to increase production and we may not be able to obtain sufficient inventory to fill orders on a timely basis. Even if we are able to increase supply to meet customer demand, we may not be able to do so in a timely manner, or our contract manufacturers may experience supply constraints. If we cannot procure sufficient supply to meet demand or otherwise fail to fulfill our customers' orders on a timely basis, or at all, our customer relationships could be damaged, we could lose revenue and market share and our reputation could be harmed. Additionally, since some of our products are part of a complex data center buildout, supply constraints or availability issues with respect to any one component have had and may have a broader revenue impact.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> If we overestimate our customers' future demand for our products, or if customers cancel or defer orders or choose to purchase from our competitors, we may not be able to reduce our inventory or other contractual purchase commitments. In the past, we have experienced a reduction in average selling prices, including due to channel pricing programs that we have implemented and may continue to implement, as a result of our overestimation of future demand, and we may need to continue these reductions. We have had to increase prices for certain of our products as a result of our suppliers' increase in prices, and we may need to continue to do so for other products in the future. We have also written down our inventory, incurred cancellation penalties, and recorded impairments and may have to do so in the future. These impacts were amplified by our placement of non-cancellable and non-returnable purchasing terms well in advance of our historical lead times and could be exacerbated if we need to make changes to the design of future products. The risk of these impacts has increased and may continue to increase as our purchase obligations and prepaids have grown and are expected to continue to grow and become a greater portion of our total supply. All of these factors may negatively impact our gross margins and financial results.

**LABEL THIS - LATER TEXT (added or changed)**

> (none: text removed)

**CONTEXT ONLY - paragraph after (unchanged)**

> Challenges in estimating demand could become more pronounced or volatile in the future on both a global and regional basis. Extended lead times may occur if we experience other supply constraints caused by natural disasters, pandemics or other events. In addition, geopolitical tensions, such as those involving Taiwan and China, which comprise a significant portion of our revenue and where we have suppliers, contract manufacturers, and assembly partners who are critical to our supply continuity, could have a material adverse impact on us.

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.75 | later filing, paragraph 49 of 209
> If we overestimate demand, or if customers cancel or defer orders or choose to purchase from our competitors, we may not be able to utilize on-hand inventory or reduce purchase commitments accordingly. We have had to reduce average selling prices, including due to our channel pricing programs, increase prices for certain of our products as a result of our suppliers' increase in prices, write down our inventory, incur cancellation penalties, and record impairments, and may have to do so in the future. These impacts would be amplified by our non-cancellable and non-returnable purchase orders placed in advance of our historical lead times and could be exacerbated if we need to make changes to the design of future products. The risk of these impacts has increased and may continue to increase as our purchase obligations and prepaids have grown and are expected to continue to grow and become a greater portion of our total supply. All of these factors may negatively impact our gross margins and financial results.
> >
> > [2] match 0.38 | later filing, paragraph 185 of 209
> Additionally, restrictions imposed by the Chinese government on the duration of gaming activities and access to games may adversely affect our Gaming revenue, and increased oversight of digital platform companies may adversely affect our Data Center revenue. The Chinese government may also encourage customers to purchase from our China-based competitors, or impose restrictions on the sale to certain customers of our products, or any products containing components made by our partners and suppliers. For example, the Chinese government announced restrictions relating to certain sales of products containing certain products made by Micron, a supplier of ours. As another example, an agency of the Chinese government announced an Action Plan that endorses new standards regarding the compute performance per watt and per memory bandwidth of accelerators used in new and renovated data centers in China. If the Chinese government modifies or implements the Action Plan in a way that effectively prevents us from being able to design products to meet the new standard, this may restrict the ability of customers to use some of our data center products and may have a material and adverse impact on our business, operating results and financial condition. Further restrictions on our products or the products of our suppliers could negatively impact our business and financial results.
> >
> > [3] match 0.38 | later filing, paragraph 126 of 209
> We acquire and invest in businesses that offer products, services and technologies that we believe will help expand or enhance our strategic objectives. Acquisitions or investments involve significant challenges and risks and could impair our ability to grow our business, develop new products or sell our products and ultimately could have a negative impact on our financial results. If we pursue a particular transaction, we may limit our ability to enter into other transactions that could help us achieve our other strategic objectives. If we are unable to timely complete acquisitions, including due to delays and challenges in obtaining regulatory approvals, we may be unable to pursue other transactions, we may not be able to retain critical talent from the target company, technology may evolve and make the acquisition less attractive, and other changes can take place, which could reduce the anticipated benefits of the transaction and negatively impact our business. Regulators could also impose conditions that reduce the ultimate value of our acquisitions. In addition, to the extent that our perceived ability to consummate acquisitions has been harmed, future acquisitions may be more difficult, complex or expensive. Further, our investments in publicly traded companies could create volatility in our results and may generate losses up to the value of the investment. In addition, we have invested and may continue to invest in private companies to further our strategic objectives and to support certain key business initiatives. These companies can include early-stage companies still defining their strategic direction. Many of the instruments in which we invest are non-marketable and illiquid at the time of our initial investment, and we are not always able to achieve a return. To the extent any of the companies in which we invest are not successful, we could recognize an impairment and/or lose all or part of our investment. Our investment portfolio contains industry sector concentration risks, and a decline in any one or multiple industry sectors could increase our impairment losses.

**Final label:** ____________  **Reason:** ____________

---

### C42 · INTC_FY2025-u028

| | label | conf | reason |
|---|---|---|---|
| Claude | `ambiguous` | 1 | New 14A-pause impairment scenario; earlier has only generic long-lived asset write-down risk, so added vs modified is unclear. |
| ChatGPT | `material_modified` | 3 | The later text adds a specific Intel 14A discontinuation scenario causing foundry-asset impairments; added_claim. |

Position: later filing paragraph 17 of 154

**CONTEXT ONLY - paragraph before (unchanged)**

> We are making significant, long-term and inherently risky investments in R&D and manufacturing facilities that may not realize a favorable return.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> (none: text added)

**LABEL THIS - LATER TEXT (added or changed)**

> ▪Losses with Respect to our Investments in R&D and Manufacturing Facilities and Equipment: We had over $100 billion of property, plant and equipment, net on our balance sheet as of December 27, 2025, the substantial majority of which we estimate relate to our foundry business. While the significant majority of this relates to our existing and in-development nodes, including Intel 18A and Intel 18A-P, with each transition to a new node we continue to utilize some R&D and manufacturing assets from prior nodes. If we were to pause or discontinue the design, development and manufacturing of Intel 14A and other next generation leading-edge nodes, we would expect to incur significant material impairments with respect to foundry assets that may impact our results of operations. For example, we would likely discontinue the new leading-edge fabrication facilities we are building in Ohio. We also would expect to incur additional costs and expenses as we wind down other projects and facilities and reduce headcount.

**CONTEXT ONLY - paragraph after (unchanged)**

> ▪Loss of Eligibility for Government Incentives. We have also entered into government incentive arrangements with local, regional and national governments, both U.S. and non-U.S. If we were to pause or discontinue the design, development and manufacturing of Intel 14A, we may lose eligibility for various incentives contemplated by these arrangements, and we may be required to repay amounts already received under these arrangements.

**CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3)**

> [1] match 0.39 | earlier filing, paragraph 11 of 174
> The investments required for our process technology roadmap and our worldwide manufacturing and assembly and test require capital expenditures above our historical levels. In recent years, the semiconductor manufacturing industry has seen very significant increases in the capital investments required for manufacturing facilities utilizing leading process technologies, including as a result of the use of EUV and high-NA EUV lithography tools. Our ownership and operation of such high-tech fabrication facilities, and our need to build new and expand existing facilities in anticipation of future demand, has resulted and will continue to result in us incurring large capital outlays and high costs that are fixed or difficult to reduce in the short term. Such capital outlays and costs include those related to utilization of existing facilities, facility construction and equipment, R&D, and the employment and training of a highly skilled workforce. To the extent customers are unwilling to pay prices to access the features that our process and product investments are expected to deliver, or if demand for our products, foundry capacity and assembly and test capacity decreases or we fail to forecast demand accurately, our gross margin and operating income can be disproportionately affected due to our high fixed cost structure, which is difficult to reduce quickly in response to lower demand and other unfavorable market factors. As we have reassessed demand and our "shell ahead" status and our financial results in the last few years have constrained our ability to make capital investments, we have delayed manufacturing facility construction or expansion projects in Ohio, Germany, Poland, Malaysia, and Israel. We could also be required to write off inventory or record excess manufacturing capacity charges, which would also lower our gross margin and operating income. To the extent the demand decrease is prolonged, our manufacturing or assembly and test capacity could be underutilized, and we may be required to write down our long-lived assets, which would increase our expenses. We may also be required to shorten the useful lives of under-used facilities and equipment and accelerate depreciation. For example, in the third quarter of 2024 we recorded $3.1 billion of charges related to non-cash impairments and the accelerated depreciation for certain manufacturing assets, a substantial majority of which related to the Intel 7 process node.
> >
> > [2] match 0.38 | earlier filing, paragraph 10 of 174
> To compete successfully, we must maintain an effective R&D program, develop new products and manufacturing processes, improve our products and processes, and make significant capital investments in new and existing manufacturing facilities, all ahead of competitors and market demand. The R&D efforts and capital investments we require are intensive as we compete across both product and process technologies and we may not have the ability to fund such investments at the level needed to be competitive. We incurred R&D expenses of $16.5 billion in 2024, $16.0 billion in 2023 and $17.5 billion in 2022. We are focusing our R&D efforts across several key areas, including process and packaging technology, our xPU products and features, AI, and software. These include ambitious initiatives, such as our efforts to introduce five new manufacturing process technologies, or nodes, in four years and our unified oneAPI portfolio of developer tools. Our investments are typically long-term and, even where successful, often do not contribute to our operating results for a number of years. We cannot guarantee that our efforts will deliver the benefits we anticipate, including as a result of our new products or technologies falling short of expectations or the offerings of competitors. For example, we previously experienced significant delays in the implementation of our 10nm process technology, and during 2020, we announced that our 7nm process technology would be delayed relative to our prior expectations. In such instances where we do not timely introduce new manufacturing process technologies that improve performance, performance per watt, transistor density, die utilization, core counts, and/or new features such as optimizations for AI and other workloads, with sufficient manufacturing yields and operational efficiency, relative to competing foundry processes, we have faced and will face cost, product performance, and time-to-market disadvantages relative to our competitors. This has in the past and may in the future result in higher operating costs, including as a result of additional costs from unused manufacturing capacity, higher leverage and borrowing costs, and pressure on our credit ratings, and adversely affect our business, financial condition and prospects. Further, we are not always able to timely or successfully develop new products, including as a result of bugs, late changes to features due to customer requests, or other design challenges. For example, in 2022, we announced that the release of Intel's 4th Gen Intel Xeon Scalable processor would be delayed from the first half of 2022 to the second half of 2022. To the extent our R&D efforts do not develop new products on schedule with improvements in areas like performance, performance per watt, die utilization, and core counts, and/or with new features such as optimizations for AI and other workloads, our competitive position can be harmed. We have adopted a disaggregated design approach for some of our future products, in which different processors and components can be manufactured on different processes and connected by advanced packaging technology into a single package. This approach introduces new areas of complexity in design and manufacturability, particularly in the deployment of advanced packaging technologies, several of which are novel, have a limited manufacturing history, and/or have increased costs. Delays or failures in implementing disaggregated designs could adversely affect our ability to timely introduce competitive products. For example, adapting a processor or component design for a new or different manufacturing process involves additional R&D expense and can result in delays in the development of the associated product and higher costs due to the utilization of more advanced and expensive capital equipment.
> >
> > [3] match 0.38 | earlier filing, paragraph 15 of 174
> We are not always successful or efficient in developing or implementing new process nodes and manufacturing processes. We experienced significant delays in implementing our 10nm process technology, and in 2020, we encountered a defect mode in the development of our 7nm process technology that resulted in delays relative to our prior expectations. In 2022, Intel's 4th Gen Intel Xeon Scalable processor was delayed to allow for more platform and product validation time. These delays have allowed competitors using third-party foundries, such as TSMC, to benefit from advancements in manufacturing processes introduced ahead of us, including improvements in performance, energy efficiency, and other features, which have helped increase the competitiveness of their products. On the product side, we have had limited market success with our accelerator offerings, and in 2024 we recognized $922 million in Gaudi AI accelerator inventory-related charges. We may experience greater adverse competitive impacts in the event of further delays in the development of future manufacturing process technologies and products or lack of market success with our offerings.

**Final label:** ____________  **Reason:** ____________

---

### C45 · AVGO_FY2024-u210

| | label | conf | reason |
|---|---|---|---|
| Claude | `boilerplate` | 2 | Earlier lead-in plus list (para 245) merged into one sentence; content present. |
| ChatGPT | `material_modified` | 2 | The later text specifies additional factors that can cause income-tax volatility. |

Position: later filing paragraph 189 of 222

**CONTEXT ONLY - paragraph before (unchanged)**

> We collect, use, store, or otherwise process personal information, which subjects us to privacy and data security laws and contractual commitments, and our actual or perceived failure to comply with such laws and commitments could harm our business.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> (none: text added)

**LABEL THIS - LATER TEXT (added or changed)**

> Our income taxes are subject to volatility and could be adversely affected by numerous factors, including reorganization or restructuring of our business, tax structure, business combinations, jurisdictional mix of our income and assets, and changes in tax legislation or accounting policies or related interpretations.

**CONTEXT ONLY - paragraph after (unchanged)**

> As a result of U.S. tax reforms, our global income is subject to tax in the U.S. and we expect an increase in our effective tax rate and our cash tax costs. In addition, many countries are implementing anti-base-erosion legislation and guidance aimed at standardizing and modernizing global corporate tax policy, including changes to cross-border tax, transfer pricing documentation rules, and nexus-based tax incentive practices. Many countries have implemented or are in the process of implementing a global minimum tax, which may materially increase our effective tax rate and cash tax costs. For example, Singapore recently adopted the global minimum tax, which will be effective for our fiscal year 2026. Substantial changes in domestic or international corporate tax policies, regulations or guidance, enforcement activities or legislative investigations and inquiries may materially adversely affect our business and impact our provision for income taxes, net income, cash flow and our results of operations generally.

**CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3)**

> [1] match 0.49 | earlier filing, paragraph 245 of 292
> Our income taxes are subject to volatility and could be adversely affected by numerous factors including:
> >
> > [2] match 0.44 | earlier filing, paragraph 237 of 292
> After the enactment of the U.S. Tax Cuts and Jobs Act (the "2017 Tax Reform Act"), most of our income is taxable in the U.S. with a significant portion taxable under the Global Intangible Low-Taxed Income ("GILTI") regime. Beginning in fiscal year 2027, the deduction allowable under the GILTI regime will decrease from 50% to 37.5%, which will increase the effective tax rate imposed on our income. The 2017 Tax Reform Act also limits our ability to deduct research and development expenses beginning in fiscal year 2023. These expenses are now capitalized and amortized over 5 years (15 years for foreign expenses), which have and may continue to materially increase our cash tax costs. The U.S. also enacted the Inflation Reduction Act of 2022 ("IRA") in August 2022, which created a new book minimum tax of at least 15% of consolidated GAAP pre-tax income for corporations with average book income in excess of $1 billion. This book minimum tax will first apply to our fiscal year 2024 and any increase in our effective tax rate or cash tax will depend on a number of factors, including any offsets for foreign tax credits or general business credits, or changes in book income following business combinations. The IRA also created an excise tax of 1% of the value of our stock repurchased after December 31, 2022. While the impact of this excise tax has not been material, it could increase materially depending on various factors, including the amount and frequency of our stock repurchases, applicability to business combination transactions, and any permitted reductions or exceptions to the amount subject to the tax. If (i) the U.S. tax rate increases, (ii) the deduction allowable under the GILTI regime is further reduced or eliminated, or (iii) additional limitations are put on our ability to deduct interest expense, our provision for income taxes, net income, and cash flows would be adversely impacted.
> >
> > [3] match 0.40 | earlier filing, paragraph 166 of 292
> Many of our existing customers have multi-year enterprise software license agreements, some of which involve substantial aggregate fee amounts. These customers often do not have a contractual obligation to purchase additional solutions. Customer renewal rates may decline or fluctuate as a result of a number of factors, including the level of customer satisfaction with our solutions or customer support, customer budgets and the pricing of our solutions as compared with the solutions offered by our competitors, any of which may cause our revenue to grow more slowly than expected, if at all. The failure to renew customer agreements of similar scope, on terms that are commercially attractive to us, could materially adversely affect our business, financial condition and operating results and cash flow.

**Final label:** ____________  **Reason:** ____________

---

### C46 · AVGO_FY2024-u238

| | label | conf | reason |
|---|---|---|---|
| Claude | `ambiguous` | 1 | Heading retained so debt-service risk persists, but refinancing and default body text not found in later filing. |
| ChatGPT | `material_removed` | 3 | The debt-payment and refinancing risk is no longer disclosed. |

Position: earlier filing paragraph 275 of 292

**CONTEXT ONLY - paragraph before (unchanged)**

> Servicing our debt requires a significant amount of cash, and we may not have sufficient cash flow from our business to pay our substantial debt.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> Our ability to make scheduled payments of the principal of, to pay interest on, and to refinance our debt, depends on our future performance, which is subject to economic, financial, competitive and other factors. Our business may not continue to generate cash flow from operations in the future sufficient to satisfy our obligations under our current indebtedness and any future indebtedness we may incur and to make necessary capital expenditures. If we are unable to generate such cash flow, we may be required to adopt one or more alternatives, such as reducing or delaying investments or capital expenditures, selling assets, refinancing or obtaining additional equity capital on terms that may be onerous or highly dilutive. Our ability to refinance our outstanding indebtedness or future indebtedness will depend on the capital markets and our financial condition at such time. We may not be able to engage in any of these activities or engage in these activities on desirable terms when needed, which could result in a default on our indebtedness.

**LABEL THIS - LATER TEXT (added or changed)**

> (none: text removed)

**CONTEXT ONLY - paragraph after (unchanged)**

> Risks Related to Owning Our Common Stock

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.35 | later filing, paragraph 47 of 222
> A general slowdown in the global economy or in a particular region or industry, other unfavorable changes in economic conditions, such as inflation, higher interest rates, tightening of the credit markets, recession or slowing growth, or an increase in trade tensions with U.S. trading partners could negatively impact our business, financial condition and liquidity. Adverse global economic conditions have from time to time caused or exacerbated significant slowdowns in the industries and markets in which we operate, which have adversely affected our business and results of operations. Macroeconomic weakness and uncertainty also make it more difficult for us to accurately forecast operating results, and may make it more difficult to raise or refinance debt. An escalation of trade tensions between the U.S. and China has resulted in trade restrictions, increased protectionism and increased tariffs that harm our ability to participate in Chinese markets or compete effectively with Chinese companies. Sustained uncertainty about, or worsening of, current global economic conditions and further escalation of trade tensions between the U.S. and its trading partners, especially China, and the decoupling of the U.S. and China economies, could result in a global economic slowdown and long-term changes to global trade. Such events may also (i) cause our customers and consumers to reduce, delay or forgo technology spending, (ii) result in customers sourcing products from other suppliers not subject to such restrictions or tariffs, (iii) lead to the insolvency or consolidation of key suppliers and customers, and (iv) intensify pricing pressures. Any or all of these factors could negatively affect demand for our products and our business, financial condition and results of operations.
> >
> > [2] match 0.35 | later filing, paragraph 187 of 222
> The manufacture and distribution of our semiconductors must comply with technical standards and a variety of domestic and international laws and regulations, including those related to the materials composition of our semiconductor products, and the use, disposal, clean-up of and human exposure to hazardous materials. This could increase the complexity and costs of our product design and procurement operations, require us to stop distributing our products commercially until they comply with such new standards, lead our customers to suspend imports of their products into that country, require us to re-engineer our products and disrupt cross-border manufacturing relationships. In addition, we may be required to modify our manufacturing process or equipment, or be restricted in our ability to expand our facilities. Any failure by us to comply with such requirements could result in litigation against us and the payment of significant fines and damages by us in the event of a significant adverse judgment. Any such event could have a material adverse effect on our business, financial condition and results of operations. Complying with any cleanup or remediation obligations for which we are or become responsible could also be costly and have a material adverse effect on our business, financial condition and results of operations.
> >
> > [3] match 0.35 | later filing, paragraph 99 of 222
> Our semiconductor customers are not generally required to purchase specific quantities of products. Even when customers agree to source an agreed portion of their product needs from us, such arrangements often include pricing schedules or methodologies that apply regardless of the volume of products purchased, and those customers may not purchase the amount of product we expect. As a result, we may not generate the amount of revenue or achieve the level of profitability we expect under such arrangements. Moreover, our top customers' purchasing power has, in some cases, given them the ability to make greater demands on us with regard to pricing and contractual terms in general. Some customers may even reduce the amount of products or decline to purchase due to their internal development of the products. The loss of, or any substantial reduction in sales to, any of our top customers, including our hyperscale customers, could have a material adverse effect on our business, financial condition, results of operations and cash flows.

**Final label:** ____________  **Reason:** ____________

---

## B. Retest (pilot units)

### R1 · NVDA_FY2025-u048

| | label | conf | reason |
|---|---|---|---|
| Claude | `boilerplate` | 2 | Paragraphs 72-73 merged; opening reworded and closing sentence restates the demand-volatility risk already stated. |
| ChatGPT | `material_modified` | 3 | Later adds a revenue-volatility consequence and expands the application wording. |

Position: earlier filing paragraph 72 of 197; later filing paragraph 72 of 209

**CONTEXT ONLY - paragraph before (unchanged)**

> Challenges in estimating demand could become more pronounced or volatile in the future on both a global and regional basis. Extended lead times may occur if we experience other supply constraints caused by natural disasters, pandemics or other events. In addition, geopolitical tensions, such as those involving Taiwan and China, which comprise a significant portion of our revenue and where we have suppliers, contract manufacturers, and assembly partners who are critical to our supply continuity, could have a material adverse impact on us.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> The use of our GPUs other than that for which they were designed and marketed, including new and unexpected use cases, has impacted and can in the future impact demand for our products, including by leading to inconsistent spikes and drops in demand. For example, several years ago, our Gaming GPUs began to be used for mining digital currencies, such as Ethereum. It is difficult for us to estimate with any reasonable degree of precision the past or current impact of cryptocurrency mining, or forecast the future impact of cryptocurrency mining, on demand for our products. Volatility in the cryptocurrency market, including new compute technologies, price changes in cryptocurrencies, government cryptocurrency policies and regulations, new cryptocurrency standards and changes in the method of verifying blockchain transactions, has impacted and can in the future impact cryptocurrency mining and demand for our products and can further impact our ability to estimate demand for our products. Changes to cryptocurrency standards and processes including, but not limited to, the Ethereum 2.0 merge in 2022, have reduced and may in the future decrease the usage of GPUs for Ethereum mining. This has created and may in the future create increased aftermarket sales of our

**LABEL THIS - LATER TEXT (added or changed)**

> The use of our GPUs for new, mercurial, or trendy applications, has impacted and can impact in the future demand for our products, including by leading to inconsistent spikes and drops in demand. For example, several years ago, our Gaming GPUs began to be used for mining digital currencies, such as Ethereum. It is difficult for us to estimate with any reasonable degree of precision the past or current impact of cryptocurrency mining, or forecast the future impact of cryptocurrency mining, on demand for our products. Volatility in the cryptocurrency market, including new compute technologies, price changes in cryptocurrencies, government cryptocurrency policies and regulations, new cryptocurrency standards and changes in the method of verifying blockchain transactions, has impacted and can in the future impact cryptocurrency mining and demand for our products and can further impact our ability to estimate demand for our products. Changes to cryptocurrency standards and processes including, but not limited to, the Ethereum 2.0 merge in 2022, have reduced and may in the future decrease the usage of GPUs for Ethereum mining. This has created and may in the future create increased aftermarket sales of our GPUs, which could negatively impact retail prices for our GPUs and reduce demand for our new GPUs. In general, our new products or previously sold products may be resold online or on the unauthorized "gray market," which also makes demand forecasting difficult. Gray market products and reseller marketplaces compete with our new products and distribution channels. Our inability to accurately predict our demand that arises from new use cases may create volatility in our revenue.

**CONTEXT ONLY - paragraph after (unchanged)**

> Dependency on third-party suppliers and their technology to manufacture, assemble, test, or package our products reduces our control over product quantity and quality, manufacturing yields, and product delivery schedules and could harm our business.

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.42 | later filing, paragraph 167 of 209
> Increasing use of economic sanctions and export controls has impacted and may in the future impact demand for our products or services, negatively impacting our business and financial results. Reduced demand due to export controls could also lead to excess inventory or cause us to incur related supply charges. Additional unilateral or multilateral controls are also likely to include deemed export control limitations that negatively impact the ability of our research and development teams to execute our roadmap or other objectives in a timely manner. Additional export restrictions may not only impact our ability to serve overseas markets, but also provoke responses from foreign governments, including China, that negatively impact our supply chain or our ability to provide our products and services to customers in all markets worldwide, which could also substantially reduce our revenue. Regulators in China have inquired about our sales and efforts to supply the China market and our fulfillment of the commitments we entered at the close of our Mellanox acquisition. For example, regulators in China are investigating whether complying with applicable U.S. export controls discriminates unfairly against customers in the China market. If regulators conclude that we have failed to fulfill such commitments or we have violated any applicable law in China, we could be subject to financial penalties, restrictions on our ability to conduct our business, restrictions regarding our networking products and services, or otherwise impact our operations in China, any of which could have a material and adverse impact on our business, operating results and financial condition.
> >
> > [2] match 0.36 | later filing, paragraph 44 of 209
> Our target markets remain competitive, and competition may intensify with expanding and changing product and service offerings, industry standards, customer and market needs, new entrants and consolidations. Our competitors' products, services and technologies, including those mentioned above in this Annual Report on Form 10-K, may be cheaper or provide better functionality or features than ours, which has resulted and may in the future result in lower-than-expected selling prices or demand for our products. Some of our competitors operate their own fabrication facilities, and have longer operating histories, larger customer bases, more comprehensive IP portfolios and patent protections, more design wins, and greater financial, sales, marketing and distribution resources than we do. These competitors may be able to acquire market share and/or prevent us from doing so, more effectively identify and capitalize upon opportunities in new markets and end-user trends, more quickly transition their products, and impinge on our ability to procure sufficient foundry capacity and scarce input materials during a supply-constrained environment, which could harm our business. Some of our customers have in-house expertise and internal development capabilities similar to some of ours and can use or develop their own solutions to replace those we are providing. For example, others may offer cloud-based services that compete with our AI cloud service offerings, and we may not be able to establish market share sufficient to achieve the scale necessary to meet our business objectives. If we are unable to successfully compete in this environment, demand for our products, services and technologies could decrease and we may not establish meaningful revenue.
> >
> > [3] match 0.35 | later filing, paragraph 166 of 209
> Export controls could disrupt our supply chain and distribution channels, negatively impacting our ability to serve demand, including in markets outside China and for our gaming products. The possibility of additional export controls has negatively impacted and may in the future negatively impact demand for our products, benefiting competitors that offer alternatives less likely to be restricted by further controls. Repeated changes in the export control rules are likely to impose compliance burdens on our business and our customers, negatively and materially impacting our business.

**CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3)**

> [1] match 0.44 | earlier filing, paragraph 73 of 197
> GPUs, which could negatively impact retail prices for our GPUs and reduce demand for our new GPUs. In general, our new products or previously sold products may be resold online or on the unauthorized "gray market," which also makes demand forecasting difficult. Gray market products and reseller marketplaces compete with our new products and distribution channels.
> >
> > [2] match 0.40 | earlier filing, paragraph 163 of 197
> Increasing use of economic sanctions and export controls has impacted and may in the future impact demand for our products or services, negatively impacting our business and financial results. Reduced demand due to export controls could also lead to excess inventory or cause us to incur related supply charges. Additional unilateral or multilateral controls are also likely to include deemed export control limitations that negatively impact the ability of our research and development teams to execute our roadmap or other objectives in a timely manner. Additional export restrictions may not only impact our ability to serve overseas markets, but also provoke responses from foreign governments, including China, that negatively impact our supply chain or our ability to provide our products and services to customers in all markets worldwide, which could also substantially reduce our revenue. Regulators in China have inquired about our sales and efforts to supply the China market and our fulfillment of the commitments we entered at the close of our Mellanox acquisition. If the regulators conclude that we have failed to fulfill such commitments or we have violated any applicable law in China, we could be subject to various penalties or restrictions on our ability to conduct our business, any of which could have a material and adverse impact on our business, operating results and financial condition.
> >
> > [3] match 0.37 | earlier filing, paragraph 66 of 197
> Our customer orders and longer-term demand estimates may change or may not be correct, as we have experienced in the past. Product transitions are complex and can impact our revenue as we often ship both new and prior architecture products simultaneously and we and our channel partners prepare to ship and support new products. Due to our product introduction cycles, we are almost always in various stages of transitioning the architecture of our Data Center, Professional Visualization, and Gaming products. We will have a broader and faster Data Center product launch cadence to meet a growing and diverse set of AI opportunities. The increased frequency of these transitions may magnify the challenges associated with managing our supply and demand due to long manufacturing lead times. Qualification time for new products, customers anticipating product transitions and channel partners reducing channel inventory of prior architectures ahead of new product introductions can create reductions or volatility in our revenue. We have experienced and may in the future experience reduced demand for current generation architectures when customers anticipate transitions, and we may be unable to sell multiple product architectures at the same time for current and future architecture transitions. If we are unable to execute our architectural transitions as planned for any reason, our financial results may be negatively impacted. The increasing frequency and complexity of newly introduced products may result in unanticipated quality or production issues that could increase the magnitude of inventory provisions, warranty or other costs or result in product delays. Deployment of new products to customers creates additional challenges due to the complexity of our technologies, which has impacted and may in the future impact the timing of customer purchases or otherwise impact our demand. While we have managed prior product transitions and have previously sold multiple product architectures at the same time, these transitions are difficult, may impair our ability to predict demand and impact our supply mix, and we may incur additional costs.

**Final label:** ____________  **Reason:** ____________

---

### R3 · AVGO_FY2024-u068

| | label | conf | reason |
|---|---|---|---|
| Claude | `boilerplate` | 2 | Parenthetical qualifier dropped; same acquisition-liability risk. |
| ChatGPT | `material_modified` | 3 | The possibility that assumed liabilities may be unexpected was dropped. |

Position: earlier filing paragraph 90 of 292; later filing paragraph 71 of 222

**CONTEXT ONLY - paragraph before (unchanged)**

> •diversion of management's attention from daily operations and the pursuit of other opportunities;

**LABEL THIS - EARLIER TEXT (removed or changed)**

> •incurring significant restructuring charges and amortization expense, assuming liabilities (some of which may be unexpected) and ongoing or new lawsuits, potential impairment of acquired goodwill and other intangible assets, and increasing our expenses and working capital requirements;

**LABEL THIS - LATER TEXT (added or changed)**

> •incurring significant restructuring charges and amortization expense, assuming liabilities and ongoing or new lawsuits, potential impairment of acquired goodwill and other intangible assets, and increasing our expenses and working capital requirements;

**CONTEXT ONLY - paragraph after (unchanged)**

> •the potential for deficiencies in internal controls of the acquired business, as well as implementing our own management information systems, operating systems and internal controls for the acquired operations;

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.37 | later filing, paragraph 182 of 222
> We collect, use and store (collectively referred to as "process" in this paragraph) a high volume, variety and velocity of certain personal information in connection with the operation of our business. This creates various levels of privacy risks across different parts of our business, depending on the type of personal information, the jurisdiction in question and the purpose of their processing. The personal information we process is subject to an increasing number of federal, state, local, and foreign laws and regulations regarding privacy and data security, as well as contractual commitments. Privacy legislation and other data protection regulations, enforcement and policy activity in this area are expanding rapidly in many jurisdictions and creating a complex regulatory compliance environment. Sectoral legislation, certification requirements and technical standards applying to certain categories of our customers, such as those in the financial services or public sector, have exacerbated this trend. The cost of complying with and implementing these privacy-related and data governance measures could increase depending on any additional burdensome security, business processes, or business record or data localization requirements. Concerns about government interference, sovereignty and expanding privacy, cybersecurity and data governance legislation could adversely affect our customers and our products and services, particularly in cloud computing, AI and our own data management practices. The theft, loss or misuse of personal data collected, used, stored or transferred by us to run our business could result in significantly increased business and security costs or costs related to defending legal claims. Any inadvertent failure or perceived failure by us to comply with privacy, data governance or cybersecurity obligations may result in governmental enforcement actions, litigation, substantial fines and damages, and could cause our customers to lose trust in us, which could have an adverse effect on our reputation and business.
> >
> > [2] match 0.36 | later filing, paragraph 194 of 222
> Our operations benefit from the various tax incentives extended to us in various jurisdictions to encourage investment or employment. Each tax incentive and tax holiday is subject to our compliance with various conditions and may, in some instances, be amended or terminated prior to their scheduled termination date by the relevant governmental authority. If we cannot, or elect not to, comply with the conditions related to our tax incentive or tax holiday, we could be required to refund previously realized material tax benefits. If such tax incentive or tax holiday is modified or terminated prior to its expiration absent a new incentive applying, we could suffer material adverse tax and other financial consequences, which would increase our expenses, reduce our profitability and adversely affect our cash flows. In addition, we may be required, or elect, to modify our operational structure and tax strategy in order to keep an incentive, which could result in a decrease in the benefits of the incentive. Adoption of global minimum tax provisions in a country in which we have an existing tax incentive could have a material adverse impact on our tax incentives. Our tax incentives and tax holiday, before taking into consideration U.S. foreign tax credits, decreased the provision for income taxes by approximately $2,261 million in the aggregate and increased diluted net income per share by $0.47 for fiscal year 2024.
> >
> > [3] match 0.35 | later filing, paragraph 155 of 222
> •the shift to cloud-based IT solutions and services, such as hyperscale computing, which may adversely affect the timing and volume of sales of our semiconductor products for use in traditional enterprise data centers;

**CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3)**

> [1] match 0.38 | earlier filing, paragraph 246 of 292
> •reorganization or restructuring of our businesses, tangible and intangible assets, outstanding indebtedness and corporate structure, including business combinations;
> >
> > [2] match 0.36 | earlier filing, paragraph 286 of 292
> These fluctuations are often unrelated or disproportionate to our operating performance. Broad market and industry fluctuations, as well as general economic, political and market conditions such as recessions, interest rate changes or currency fluctuations, may negatively impact the market price of our common stock. You may not realize any return on your investment in us and may lose some or all of your investment. In the past, companies that have experienced volatility in the market price of their stock have been subject to securities class action litigation. We may be the target of this type of litigation in the future. In addition, we have been, and in the future we may be, subject to lawsuits stemming from our acquisitions, including the VMware Merger. Securities litigation against us, including the lawsuits related to such acquisitions, could result in substantial costs and divert our management's attention from other business concerns, which could seriously harm our business.
> >
> > [3] match 0.36 | earlier filing, paragraph 275 of 292
> Our ability to make scheduled payments of the principal of, to pay interest on, and to refinance our debt, depends on our future performance, which is subject to economic, financial, competitive and other factors. Our business may not continue to generate cash flow from operations in the future sufficient to satisfy our obligations under our current indebtedness and any future indebtedness we may incur and to make necessary capital expenditures. If we are unable to generate such cash flow, we may be required to adopt one or more alternatives, such as reducing or delaying investments or capital expenditures, selling assets, refinancing or obtaining additional equity capital on terms that may be onerous or highly dilutive. Our ability to refinance our outstanding indebtedness or future indebtedness will depend on the capital markets and our financial condition at such time. We may not be able to engage in any of these activities or engage in these activities on desirable terms when needed, which could result in a default on our indebtedness.

**Final label:** ____________  **Reason:** ____________

---

### R4 · NVDA_FY2025-u003

| | label | conf | reason |
|---|---|---|---|
| Claude | `boilerplate` | 2 | Summary bullet updated to repeat the reworded heading; lead-time risk already stated in earlier body. |
| ChatGPT | `material_modified` | 3 | The later text adds manufacturing lead times and supply uncertainty as causes. |

Position: earlier filing paragraph 6 of 197; later filing paragraph 6 of 209

**CONTEXT ONLY - paragraph before (unchanged)**

> Risks Related to Demand, Supply and Manufacturing

**LABEL THIS - EARLIER TEXT (removed or changed)**

> •Failure to estimate customer demand accurately has led and could lead to mismatches between supply and demand.

**LABEL THIS - LATER TEXT (added or changed)**

> •Long manufacturing lead times and uncertain supply and component availability, combined with a failure to estimate customer demand accurately has led and could lead to mismatches between supply and demand.

**CONTEXT ONLY - paragraph after (unchanged)**

> •Dependency on third-party suppliers and their technology to manufacture, assemble, test, or package our products reduces our control over product quantity and quality, manufacturing yields, and product delivery schedules and could harm our business.

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.69 | later filing, paragraph 46 of 209
> Long manufacturing lead times and uncertain supply and component availability, combined with a failure to estimate customer demand accurately, has led and could lead to mismatches between supply and demand.
> >
> > [2] match 0.46 | later filing, paragraph 48 of 209
> If we inaccurately estimate demand, or our customers change orders, as we have experienced in the past, we may not be able to reduce our supply commitments in time, at the same rate, or at all. Significant mismatches between supply and demand have varied across our market platforms, resulted in both product shortages and excess inventory, significantly harmed our financial results and could reoccur. If we underestimate demand, and our foundry partners and contract manufacturers are unable to increase production or provide sufficient supply, we may not be able to meet increased customer demand in a timely manner, or at all. Our reputation and customer relationships could be damaged and we could lose revenue and market share. Additionally, since some of our products are part of a complex data center buildout, supply constraints or availability issues with respect to any one component have had and may have a broader revenue impact. For example, our ability to sell certain products has been and could be impeded if components necessary for the finished products are not available from third parties.
> >
> > [3] match 0.44 | later filing, paragraph 138 of 209
> •exposure to additional cybersecurity risks and vulnerabilities; and

**CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3)**

> [1] match 0.69 | earlier filing, paragraph 47 of 197
> Failure to estimate customer demand accurately has led and could lead to mismatches between supply and demand.
> >
> > [2] match 0.51 | earlier filing, paragraph 48 of 197
> We use third parties to manufacture and assemble our products, and we have long manufacturing lead times. We are not provided guaranteed wafer, component and capacity supply, and our supply deliveries and production may be non-linear within a quarter or year. If our estimates of customer demand are inaccurate, as we have experienced in the past, there could be a significant mismatch between supply and demand. This mismatch has resulted in both product shortages and excess inventory, has varied across our market platforms, and has significantly harmed our financial results.
> >
> > [3] match 0.42 | earlier filing, paragraph 68 of 197
> If we underestimate our customers' future demand for our products, our foundry partners may not have adequate lead-time or capacity to increase production and we may not be able to obtain sufficient inventory to fill orders on a timely basis. Even if we are able to increase supply to meet customer demand, we may not be able to do so in a timely manner, or our contract manufacturers may experience supply constraints. If we cannot procure sufficient supply to meet demand or otherwise fail to fulfill our customers' orders on a timely basis, or at all, our customer relationships could be damaged, we could lose revenue and market share and our reputation could be harmed. Additionally, since some of our products are part of a complex data center buildout, supply constraints or availability issues with respect to any one component have had and may have a broader revenue impact.

**Final label:** ____________  **Reason:** ____________

---

### R5 · INTC_FY2025-u016

| | label | conf | reason |
|---|---|---|---|
| Claude | `boilerplate` | 1 | Innovation-cost and asset write-down risks appear in later paragraphs 9, 12 and 17; only the Intel 7 example wording is not carried verbatim. |
| ChatGPT | `material_modified` | 2 | The specific Intel 7 write-down event and related detail are no longer stated. |

Position: earlier filing paragraph 16 of 174

**CONTEXT ONLY - paragraph before (unchanged)**

> We are not always successful or efficient in developing or implementing new process nodes and manufacturing processes. We experienced significant delays in implementing our 10nm process technology, and in 2020, we encountered a defect mode in the development of our 7nm process technology that resulted in delays relative to our prior expectations. In 2022, Intel's 4th Gen Intel Xeon Scalable processor was delayed to allow for more platform and product validation time. These delays have allowed competitors using third-party foundries, such as TSMC, to benefit from advancements in manufacturing processes introduced ahead of us, including improvements in performance, energy efficiency, and other features, which have helped increase the competitiveness of their products. On the product side, we have had limited market success with our accelerator offerings, and in 2024 we recognized $922 million in Gaudi AI accelerator inventory-related charges. We may experience greater adverse competitive impacts in the event of further delays in the development of future manufacturing process technologies and products or lack of market success with our offerings.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> Our efforts to innovate involve significant expense and carry inherent risks, including difficulties in designing and developing next-generation process and packaging technologies, and investments in manufacturing assets and facilities that are made years in advance. We cannot guarantee that we will realize the expected benefits of next-generation process technologies, including the expected cost, performance, power, and density advantages, or that we will achieve an adequate return on our capital and R&D investments, particularly as the development of new nodes has grown increasingly expensive. In such circumstances, we may be required to write down the value of some of our manufacturing assets and facilities, increasing our expenses, as we were required to do in the third quarter of 2024 with respect to the Intel 7 process node.

**LABEL THIS - LATER TEXT (added or changed)**

> (none: text removed)

**CONTEXT ONLY - paragraph after (unchanged)**

> Changes in product demand and margins can adversely affect our financial results.

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.40 | later filing, paragraph 9 of 154
> To compete successfully, we must maintain an effective R&D program, develop new products and manufacturing processes, improve our products and processes and make significant capital investments in new and existing manufacturing facilities, all ahead of competitors and market demand. The R&D efforts and capital investments we require are significant as we compete across both product and process technologies and we may not have the ability to fund such investments at the level needed to be competitive. We incurred R&D expenses of $13.8 billion in 2025, $16.5 billion in 2024 and $16.0 billion in 2023. We are focusing our R&D efforts across several key areas, including process and packaging technology, our xPU products and features, AI and software. Our investments are typically long-term and, even where successful, often do not contribute to our operating results for a number of years. We cannot guarantee that our efforts will deliver the benefits we anticipate, including as a result of our new products or technologies falling short of expectations or the offerings of competitors. In recent years, we have had a number of delays in the release of new products, including as a result of defects or errata, late changes to features due to customer requests, or other design challenges for our products. We have similarly had delays in our development of new process technologies and advanced packaging techniques, including with respect to performance and yield. These delays have allowed competitors using third-party foundries, such as TSMC, to benefit from advancements in manufacturing processes introduced ahead of us, including improvements in performance, energy efficiency and other features, which have helped increase the competitiveness of their products. We also missed the significant shift in compute demand to GPUs optimized for AI workloads and have been unsuccessful to date in becoming a meaningful participant in that market while certain of our key competitors have been highly successful in that market. Our most recent efforts to compete in the accelerator market with our Gaudi AI accelerators was unsuccessful, as a result of which we recognized Gaudi AI accelerator inventory-related charges of $375 million in 2025 and $922 million in 2024. To the extent we do not timely introduce new products and manufacturing process technologies that improve performance, performance per watt, transistor density, die utilization, core counts and/or new features such as optimizations for AI and other workloads, with sufficient manufacturing yields and operational efficiency, relative to competitors and competing foundry processes, we have faced and will face cost, product performance and time-to-market disadvantages relative to our competitors. This has in the past and may in the future result in higher operating costs, including as a result of additional costs from unused manufacturing capacity, higher leverage and borrowing costs and pressure on our credit ratings.
> >
> > [2] match 0.38 | later filing, paragraph 17 of 154
> ▪Losses with Respect to our Investments in R&D and Manufacturing Facilities and Equipment: We had over $100 billion of property, plant and equipment, net on our balance sheet as of December 27, 2025, the substantial majority of which we estimate relate to our foundry business. While the significant majority of this relates to our existing and in-development nodes, including Intel 18A and Intel 18A-P, with each transition to a new node we continue to utilize some R&D and manufacturing assets from prior nodes. If we were to pause or discontinue the design, development and manufacturing of Intel 14A and other next generation leading-edge nodes, we would expect to incur significant material impairments with respect to foundry assets that may impact our results of operations. For example, we would likely discontinue the new leading-edge fabrication facilities we are building in Ohio. We also would expect to incur additional costs and expenses as we wind down other projects and facilities and reduce headcount.
> >
> > [3] match 0.36 | later filing, paragraph 12 of 154
> The investments required for our leading-edge process technology development and our worldwide manufacturing and assembly and test require capital expenditures above our historical levels. In recent years, the semiconductor manufacturing industry has seen very significant increases in the capital investments required for manufacturing facilities utilizing leading-edge process technologies, including as a result of the use of EUV and high-NA EUV lithography tools. Our ownership and operation of such high-tech fabrication facilities, and our need to build new and expand or upgrade existing facilities in anticipation of future products and demand, has resulted and will continue to result in our incurring large capital outlays and high costs that are fixed or difficult to reduce in the short term. Such capital outlays and costs include those related to utilization of existing facilities, facility construction and equipment, R&D, and the employment and training of a highly skilled workforce. To the extent customers are unwilling to pay prices to access the features that our process and product investments are expected to deliver, or if demand for our products, foundry capacity and assembly and test capacity decreases or we fail to forecast demand accurately, our gross margin and operating income can be disproportionately affected due to our high fixed cost structure, which is difficult to reduce quickly in response to lower demand and other unfavorable market factors. As we have reassessed demand and our "shell ahead" strategy, and our financial results in the last few years have constrained our ability to make capital investments, we have delayed or cancelled manufacturing facility construction or expansion projects in Ohio, Germany, Poland, Malaysia and Israel and initiated the consolidation of our assembly and test facility in Costa Rica into our other facilities. We could also be required to write off inventory or record excess manufacturing capacity charges, which would also lower our gross margin and operating income. To the extent the demand decrease is prolonged, our manufacturing or assembly and test capacity could be underutilized, and we may be required to write down our long-lived assets, which would increase our expenses. We may also be required to shorten the useful lives of under-used facilities and equipment and accelerate depreciation. For example, in 2025 and 2024 we recorded $950 million and $3.3 billion, respectively, of charges related to non-cash impairments and the accelerated depreciation for certain manufacturing assets that were determined to have no remaining or reduced operational use.

**Final label:** ____________  **Reason:** ____________

---

### R12 · NVDA_FY2025-u116

| | label | conf | reason |
|---|---|---|---|
| Claude | `boilerplate` | 2 | Heading adds burden and; same litigation risk. |
| ChatGPT | `material_modified` | 2 | The later wording adds burden as an exposure beyond the previously stated risks. |

Position: earlier filing paragraph 190 of 197; later filing paragraph 206 of 209

**CONTEXT ONLY - paragraph before (unchanged)**

> Our future effective tax rate may also be affected by a variety of factors, including changes in our business or statutory rates, the mix of earnings in countries with differing statutory tax rates, available tax incentives, credits and deductions, the expiration of statutes of limitations, changes in accounting principles, adjustments to income taxes upon finalization of tax returns, increases in expenses not deductible for tax purposes, the estimates of our deferred tax assets and liabilities and deferred tax asset valuation allowances, changing interpretation of existing laws or regulations, the impact of accounting for business combinations, as well as changes in the domestic or international organization of our business and structure. Furthermore, the tax effects of accounting for stock-based compensation and volatility in our stock price may significantly impact our effective tax rate in the period in which they occur. A decline in our stock price may result in reduced future tax benefits from stock-based compensation, increase our effective tax rate and adversely affect our financial results.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> Our business is exposed to the risks associated with litigation, investigations and regulatory proceedings.

**LABEL THIS - LATER TEXT (added or changed)**

> Our business is exposed to the burden and risks associated with litigation, investigations and regulatory proceedings.

**CONTEXT ONLY - paragraph after (unchanged)**

> We currently and will likely continue to face legal, administrative and regulatory proceedings, claims, demands and/or investigations involving shareholder, consumer, competition and/or other issues relating to our business. For example, we are defending a securities class action lawsuit from multiple shareholders asserting claims that we and certain of our officers made false and/or misleading statements related to channel inventory and the impact of cryptocurrency mining on GPU demand in 2017 and 2018. Litigation and regulatory proceedings are inherently uncertain, and adverse rulings could occur, including monetary damages or fines, or an injunction stopping us from manufacturing or selling certain products, engaging in certain business practices, or requiring other remedies, such as compulsory licensing of patents. An unfavorable outcome or settlement may result in a material adverse impact. Regardless of the outcome, litigation can be costly, time-consuming, and disruptive to our operations.

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.94 | later filing, paragraph 27 of 209
> •Our business is exposed to the burden and risks associated with litigation, investigations, and regulatory proceedings.
> >
> > [2] match 0.46 | later filing, paragraph 80 of 209
> •failure by our suppliers to comply with our policies and expectations and emerging regulatory requirements;
> >
> > [3] match 0.45 | later filing, paragraph 200 of 209
> We are also bound by certain contractual obligations related to data privacy and security, and our efforts to comply with such obligations may not be successful or may be claimed to be non-compliant. For example, certain privacy laws, such as the GDPR and the CCPA, require our customers to impose specific contractual restrictions on their service providers. We sometimes host personal data in collaboration with our customers, and if a breach exposed or altered that personal data, it could harm those customer relationships and subject us to litigation, regulatory action, or fines. We publish privacy policies, marketing materials and other statements, such as compliance with certain certifications or self-regulatory principles, regarding data privacy and security. Regulators in the U.S. are increasingly scrutinizing these statements, and if these policies, materials or statements are found to be deficient, lacking in transparency, deceptive, unfair or misrepresentative of our practices, we may be subject to investigation, enforcement actions by regulators or other adverse consequences.

**CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3)**

> [1] match 0.94 | earlier filing, paragraph 27 of 197
> •Our business is exposed to the risks associated with litigation, investigations, and regulatory proceedings.
> >
> > [2] match 0.51 | earlier filing, paragraph 119 of 197
> Our business and those of our suppliers and customers may also be subject to climate-related laws, regulations and lawsuits. New or proposed regulations relating to carbon taxes, fuel or energy taxes, pollution limits, sustainability-related disclosure and governance and supply chain governance could result in greater direct costs, including costs associated with changes to manufacturing processes or the procurement of raw materials used in manufacturing processes, increased capital expenditures to improve facilities and equipment, and higher compliance and energy costs to reduce emissions, other compliance costs, as well as greater indirect costs resulting from our customers and/or suppliers incurring additional compliance costs that are passed on to us. These costs and restrictions could harm our business and results of operations by increasing our expenses or requiring us to alter our operations and product design activities.
> >
> > [3] match 0.44 | earlier filing, paragraph 179 of 197
> We are subject to stringent and changing data privacy and security laws, rules, regulations and other obligations. These areas could damage our reputation, deter current and potential customers, affect our product design, or result in legal or regulatory proceedings and liability.

**Final label:** ____________  **Reason:** ____________

---

### R14 · AVGO_FY2024-u243

| | label | conf | reason |
|---|---|---|---|
| Claude | `ambiguous` | 1 | Broad market and industry fluctuation risk to stock price existed in earlier filing; cannot tell if competitor-related part is new. |
| ChatGPT | `boilerplate` | 2 | The added summary risk is represented by existing market and competitive risks elsewhere. |

Position: later filing paragraph 213 of 222

**CONTEXT ONLY - paragraph before (unchanged)**

> •issuance of new or updated research or other reports by securities analysts;

**LABEL THIS - EARLIER TEXT (removed or changed)**

> (none: text added)

**LABEL THIS - LATER TEXT (added or changed)**

> •broad market, industry and competitor-related fluctuations;

**CONTEXT ONLY - paragraph after (unchanged)**

> •unsubstantiated news reports or other inaccurate publicity regarding us or our business;

**CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3)**

> [1] match 0.47 | earlier filing, paragraph 29 of 292
> •Our operating results are subject to substantial quarterly and annual fluctuations.
> >
> > [2] match 0.46 | earlier filing, paragraph 182 of 292
> Our operating results are subject to substantial quarterly and annual fluctuations.
> >
> > [3] match 0.43 | earlier filing, paragraph 198 of 292
> In addition, the trend toward consolidation is changing the competitive landscape. We expect this trend to continue, which may result in combined competitors having greater resources than us. Some of our competitors may also receive financial and other support from their home country government or may have a greater presence in key markets, a larger customer base, a more comprehensive IP portfolio or better patent protection than us.

**Final label:** ____________  **Reason:** ____________

---

### R23 · INTC_FY2025-u018

| | label | conf | reason |
|---|---|---|---|
| Claude | `boilerplate` | 2 | Disaggregated design supply risk largely restated in later paragraph 11. |
| ChatGPT | `material_modified` | 3 | The disaggregated-design risk remains but its logistical exposures and details changed. |

Position: earlier filing paragraph 18 of 174

**CONTEXT ONLY - paragraph before (unchanged)**

> Risks inherent in the development of next-generation process technologies include production timing delays, lower-than-anticipated manufacturing yields, longer manufacturing throughput times, failure to achieve expected performance, power, and area improvements, and product defects and errata (deviations from published specifications). Production timing delays have at times caused us to miss customer product design windows, which can result in lost revenue opportunities and damage to our customer relationships. Furthermore, when the introduction of next-generation process nodes is delayed, adding cores or other competitive features to our products can result in larger die size products, manufacturing supply constraints, and increased product costs. Lower manufacturing yields and longer manufacturing throughput times, compared to previous process nodes, can increase our product costs, adversely affect our gross margins, and contribute to manufacturing supply constraints. A new process node typically has higher costs compared to a mature node due to factors that include higher depreciation costs and lower yields, and costs and yields at times do not improve at the same rate as on prior nodes. In addition, the cost of new leading-edge process nodes continues to increase at a higher rate relative to legacy process nodes due to a number of factors, including the cost of procuring and operating advanced manufacturing equipment. As the die size of our products has increased and our manufacturing process nodes have increased the number of transistors per die, our products and manufacturing processes have grown increasingly complex and more susceptible to product defects and errata, which at times also contribute to production timing delays and lower yields that may also increase our costs to manufacture and warranty our products.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> Our disaggregated design strategy poses increased logistical risks and challenges, particularly where we decide to manufacture different product components on different process technologies, including third-party foundries' process technologies. To combine components in a single package, they need to be manufactured on a timely basis and in sufficient quantities, while the manufacturing processes we utilize may have differing yields, throughput times, and capacity constraints. We may be required to safely store some components pending the manufacture of others. Delays or quality issues with one component could limit our ability to manufacture the entire completed product. In addition, the packaging technologies used to combine these components can increase our costs and may introduce additional complexity and quality issues. To the extent we are unable to manage these risks, our ability to timely supply competitive products can be harmed and our costs could increase.

**LABEL THIS - LATER TEXT (added or changed)**

> (none: text removed)

**CONTEXT ONLY - paragraph after (unchanged)**

> Changes in product demand and margins can adversely affect our financial results.

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.42 | later filing, paragraph 11 of 154
> We have adopted a disaggregated design architecture for most of our newer and more high-end products and a number of our future products in which different processors and components, or tiles, can be manufactured on different processes and connected by advanced packaging technology into a single package. This approach introduces new areas of complexity in design and manufacturability, particularly in the deployment of advanced packaging technologies, several of which are novel, have a limited manufacturing history or have increased costs. Delays or failures in implementing disaggregated designs or the individual components thereof could adversely affect our ability to timely introduce competitive products. Further, some of our newer and more high-end products and a number of our future products involve the use of tiles manufactured by TSMC, a key competitor on the foundry side of our business, or other third-party foundry suppliers. To the extent there is any interruption in the supply of tiles manufactured by TSMC or any other third-party foundry supplier, whether as a result of a dispute or otherwise, we would be unable to complete assembly of complete products requiring such tiles until such time as we could design and manufacture replacement tiles and source such tiles from an alternative supplier, which would likely involve a substantial delay given the bespoke design of each tile to the particular manufacturing process utilized. As such, our disaggregated design approach involves significant supply chain risk to our ability to manufacture and sell our products that could have a material adverse impact on business and financial results. Further, to the extent we adopt a disaggregated design approach for products that compete with competitors' products that use a more traditional monolithic chip design, we may be at a significant cost disadvantage that adversely impacts the profitability or the success of our products.
> >
> > [2] match 0.38 | later filing, paragraph 99 of 154
> Cyber attack attempts are increasing in number, magnitude and technical sophistication, and if successful, may expose us and the affected parties to loss or misuse of proprietary or confidential information or disruptions to our supply chain or business operations, including our manufacturing operations, and could impact our financial results. We expect emerging technologies to contribute to the increasing sophistication of attacks and to lead to new threats. For example, threat actors are leveraging emerging AI technologies to develop new hacking tools and attack vectors, exploit vulnerabilities, obscure their activities and increase the difficulty of threat attribution. The proliferation of generative AI increases the risk of these technologies being used by threat actors to impersonate authorized individuals, which may make attacks even more difficult to detect and prevent. Moreover, the increased adoption of generative AI models within our internal systems, processes and tools may create new attack methods for threat actors.
> >
> > [3] match 0.37 | later filing, paragraph 79 of 154
> We utilize third-party foundries and component suppliers to manufacture or supply a number of our products and components necessary for our products that we manufacture. As part of our strategy, we expect to continue to rely upon third-party foundries. Delays in the development of foundries' future manufacturing processes could delay the introduction of products or components we design for such processes, and insufficient foundry capacity could prevent us from meeting customer demand. We typically have less control over delivery schedules, design and manufacturing co-optimization, yields, quality, product quantities and costs for components and products that are manufactured by third parties.

**Final label:** ____________  **Reason:** ____________

---

### R30 · AVGO_FY2024-u065

| | label | conf | reason |
|---|---|---|---|
| Claude | `boilerplate` | 2 | Merges the next sentence from the earlier filing; adds only a generic effect phrase. |
| ChatGPT | `material_modified` | 3 | added_claim |

Position: earlier filing paragraph 86 of 292; later filing paragraph 67 of 222

**CONTEXT ONLY - paragraph before (unchanged)**

> We may pursue acquisitions, investments, joint ventures and dispositions, which could adversely affect our results of operations.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> Our growth strategy includes acquiring or investing in businesses that offer complementary products, services and technologies, or enhance our market coverage or technological capabilities.

**LABEL THIS - LATER TEXT (added or changed)**

> Our growth strategy includes acquiring or investing in businesses that offer complementary products, services and technologies, or enhancing our market coverage or technological capabilities. Any acquisitions we may undertake, including the VMware Merger, and their integration involve risks and uncertainties, which could impede the execution of our business strategy, such as:

**CONTEXT ONLY - paragraph after (unchanged)**

> •U.S. and non-U.S. regulatory approval may take longer than anticipated, not be forthcoming or contain burdensome conditions;

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.41 | later filing, paragraph 138 of 222
> Many of our software products and services are based on data center virtualization and related hybrid-cloud technologies used to manage distributed computing architectures, which form the foundation for hybrid-cloud computing. Enabling businesses to modernize applications and efficiently implement their hybrid-cloud services presents new and difficult technological, operational and compliance challenges. If businesses build new or shift existing compute workloads off-premises to public cloud providers, this could limit the market for on-premises deployments of our data center virtualization products. Current and future customers may not perceive benefits associated with adopting our hybrid-cloud and enterprise-grade private cloud platform or our simplified product portfolios. If demand is significantly less than anticipated or we fail to realize the expected returns on our business strategy, our business, financial condition, results of operations and cash flows may be adversely affected.
> >
> > [2] match 0.40 | later filing, paragraph 135 of 222
> Although we continually seek to improve our countermeasures to prevent such incidents, we may be unable to anticipate every scenario and it is possible that certain cyber threats or vulnerabilities will be undetected or unmitigated in time to prevent an attack or an accidental incident on us and our customers. Additionally, efforts by malicious cyber actors or others could cause interruptions, delays or cessation of our product licensing, or modification of our software, which could cause us to lose existing or potential customers.
> >
> > [3] match 0.39 | later filing, paragraph 171 of 222
> Our gross margin is highly dependent on product mix, which is susceptible to seasonal and other fluctuations in our markets. A shift in sales mix away from our higher margin products, as well as the timing and amount of our software licensing and non-product revenue, could adversely affect our future gross margin percentages. In addition, increased competition and the existence of product alternatives, more complex engineering requirements, lower demand, industry oversupply or reductions in our technological lead compared to our competitors, and other factors have in the past and may in the future lead to further price erosion, lower revenue and lower margin. Conversely, periods of robust demand that create a supply imbalance can lead to higher gross margins that may not be sustainable over the longer term.

**CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3)**

> [1] match 0.55 | earlier filing, paragraph 87 of 292
> Any acquisitions we may undertake, including the VMware Merger, and their integration involve risks and uncertainties, such as:
> >
> > [2] match 0.42 | earlier filing, paragraph 85 of 292
> We may pursue acquisitions, investments, joint ventures and dispositions, which could adversely affect our results of operations.
> >
> > [3] match 0.41 | earlier filing, paragraph 7 of 292
> •We may pursue acquisitions, investments, joint ventures and dispositions, which could adversely affect our results of operations.

**Final label:** ____________  **Reason:** ____________

---

### R32 · NVDA_FY2025-u023

| | label | conf | reason |
|---|---|---|---|
| Claude | `material_modified` | 2 | Moved from earlier para 69; impacts that were amplified became would be amplified (status dropped). |
| ChatGPT | `boilerplate` | 3 | The added risk is already disclosed in the earlier filing. |

Position: later filing paragraph 49 of 209

**CONTEXT ONLY - paragraph before (unchanged)**

> Competition could adversely impact our market share and financial results.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> (none: text added)

**LABEL THIS - LATER TEXT (added or changed)**

> If we overestimate demand, or if customers cancel or defer orders or choose to purchase from our competitors, we may not be able to utilize on-hand inventory or reduce purchase commitments accordingly. We have had to reduce average selling prices, including due to our channel pricing programs, increase prices for certain of our products as a result of our suppliers' increase in prices, write down our inventory, incur cancellation penalties, and record impairments, and may have to do so in the future. These impacts would be amplified by our non-cancellable and non-returnable purchase orders placed in advance of our historical lead times and could be exacerbated if we need to make changes to the design of future products. The risk of these impacts has increased and may continue to increase as our purchase obligations and prepaids have grown and are expected to continue to grow and become a greater portion of our total supply. All of these factors may negatively impact our gross margins and financial results.

**CONTEXT ONLY - paragraph after (unchanged)**

> Factors that have caused and/or could in the future cause us to underestimate or overestimate demand, and impact the timing and volume of our revenue, include:

**CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3)**

> [1] match 0.82 | earlier filing, paragraph 69 of 197
> If we overestimate our customers' future demand for our products, or if customers cancel or defer orders or choose to purchase from our competitors, we may not be able to reduce our inventory or other contractual purchase commitments. In the past, we have experienced a reduction in average selling prices, including due to channel pricing programs that we have implemented and may continue to implement, as a result of our overestimation of future demand, and we may need to continue these reductions. We have had to increase prices for certain of our products as a result of our suppliers' increase in prices, and we may need to continue to do so for other products in the future. We have also written down our inventory, incurred cancellation penalties, and recorded impairments and may have to do so in the future. These impacts were amplified by our placement of non-cancellable and non-returnable purchasing terms well in advance of our historical lead times and could be exacerbated if we need to make changes to the design of future products. The risk of these impacts has increased and may continue to increase as our purchase obligations and prepaids have grown and are expected to continue to grow and become a greater portion of our total supply. All of these factors may negatively impact our gross margins and financial results.
> >
> > [2] match 0.38 | earlier filing, paragraph 123 of 197
> We have acquired and invested and may continue to do so in businesses that offer products, services and technologies that we believe will help expand or enhance our strategic objectives. Acquisitions or investments involve significant challenges and risks and could impair our ability to grow our business, develop new products or sell our products and ultimately could have a negative impact on our financial results. If we pursue a particular transaction, we may limit our ability to enter into other transactions that could help us achieve our other strategic objectives. If we are unable to timely complete acquisitions, including due to delays and challenges in obtaining regulatory approvals, we may be unable to pursue other transactions, we may not be able to retain critical talent from the target company, technology may evolve and make the acquisition less attractive, and other changes can take place, which could reduce the anticipated benefits of the transaction and negatively impact our business. Regulators could also impose conditions that reduce the ultimate value of our acquisitions. In addition, to the extent that our perceived ability to consummate acquisitions has been harmed, future acquisitions may be more difficult, complex or expensive. Further, our investments in publicly traded companies could create volatility in our results and may generate losses up to the value of the investment. In addition, we have invested and may continue to invest in private companies to further our strategic objectives and to support certain key business initiatives. These companies can include early-stage companies still defining their strategic direction. Many of the instruments in which we invest are non-marketable and illiquid at the time of our initial investment, and we are not always able to achieve a return. To the extent any of the companies in which we invest are not successful, we could recognize an impairment and/or lose all or part of our investment. Our investment portfolio contains industry sector concentration risks, and a decline in any one or multiple industry sectors could increase our impairment losses. We face additional risks related to acquisitions and strategic investments, including the diversion of capital and other resources, including management's attention; difficulty in realizing a satisfactory return and uncertainties to realize the benefits of an acquisition or strategic investment, if at all; difficulty or inability in obtaining governmental, regulatory approval or restrictions or other consents and approvals or financing; legal proceedings initiated as a result of an acquisition or investment; and potential failure of our due diligence processes to identify significant issues with the assets or company in which we are investing or are acquiring.
> >
> > [3] match 0.36 | earlier filing, paragraph 156 of 197
> We are subject to laws and regulations domestically and worldwide, affecting our operations in areas including, but not limited to, IP ownership and infringement; taxes; import and export requirements and tariffs; anti-corruption, including the Foreign Corrupt Practices Act; business acquisitions; foreign exchange controls and cash repatriation restrictions; data privacy requirements; competition and antitrust; advertising; employment; product regulations; cybersecurity; environmental, health, and safety requirements; the responsible use of AI; sustainability; cryptocurrency; and consumer laws. Compliance with such requirements can be onerous and expensive, could impact our competitive position, and may negatively impact our business operations and ability to manufacture and ship our products. There can be no assurance that our employees, contractors, suppliers, customers or agents will not violate applicable laws or the policies, controls, and procedures that we have designed to help ensure compliance with such laws, and violations could result in fines, criminal sanctions against us, our officers, or our employees, prohibitions on the conduct of our business, and damage to our reputation. Changes to the laws, rules and regulations to which we are subject, or changes to their interpretation and enforcement, could lead to materially greater compliance and other costs and/or further restrictions on our ability to manufacture and supply our products and operate our business. For example, we may face increased compliance costs as a result of changes or increases in antitrust legislation, regulation, administrative rule making, increased focus from regulators on cybersecurity vulnerabilities and risks. Our position in markets relating to AI has led to increased interest in our business from regulators worldwide, including the European Union, the United States, the United Kingdom and China. For example, the French Competition Authority collected information from us regarding our business and competition in the graphics card and cloud service provider market as part of an ongoing inquiry into competition in those markets. We have also received requests for information from regulators in the European Union, the United Kingdom, and China regarding our sales of GPUs, our efforts to allocate supply, foundation models and our investments, partnerships and other agreements with companies developing foundation models, and we expect to receive additional requests for information in the future. Governments and regulators are considering imposing restrictions on the hardware, software, and systems used to develop frontier foundation models and generative AI. If implemented, such restrictions could increase the costs and burdens to us and our customers, delay or halt deployment of new systems using our products, and reduce the number of new entrants and customers, negatively impacting our business and financial results. Revisions to laws or regulations or their interpretation and enforcement could also result in increased taxation, trade sanctions, the imposition of or increase to import duties or tariffs, restrictions and controls on imports or exports, or other retaliatory actions, which could have an adverse effect on our business plans or impact the timing of our shipments. Additionally, changes in the public perception of governments in the regions where we operate or plan to operate could negatively impact our business and results of operations.

**Final label:** ____________  **Reason:** ____________

---

### R33 · AVGO_FY2024-u109

| | label | conf | reason |
|---|---|---|---|
| Claude | `boilerplate` | 2 | Disruption risk with the same causes still present in later para 116. |
| ChatGPT | `material_modified` | 3 | The later disclosure changes the facility scope and adds an explicit statement about prior immaterial effects. |

Position: earlier filing paragraph 130 of 292

**CONTEXT ONLY - paragraph before (unchanged)**

> If any of the foregoing circumstances occur, we may be unable to meet our customer demand, or to the same extent as our competitors, fail to meet our contractual obligations or forgo revenue opportunities. This could damage our relationships with our customers or result in litigation for alleged failure to meet our obligations, payment of significant damages, and our net revenue could decline, adversely affecting our business, financial condition, results of operations and gross margin.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> Further, any substantial disruption in the contract manufacturing services that we utilize, including TSMC's supply of wafers to us, as a result of a natural disaster, climate change, water shortages, political unrest, military conflicts, geopolitical turmoil, trade tensions, government orders, labor shortages, medical epidemics, such as the COVID-19 pandemic, economic instability, equipment failure or other cause, could materially harm our business, customer relationships and results of operations.

**LABEL THIS - LATER TEXT (added or changed)**

> (none: text removed)

**CONTEXT ONLY - paragraph after (unchanged)**

> Failure to adjust our manufacturing and supply chain to accurately meet customer demand could adversely affect our results of operations.

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.61 | later filing, paragraph 116 of 222
> A prolonged disruption at or shut-down of one or more of our manufacturing facilities or warehouses or those of our CMs or suppliers, due to natural- or man-made disasters or other events outside of our control, such as climate change, water shortages, political unrest, military conflicts, geopolitical turmoil, trade tensions, government orders, labor shortages, medical epidemics, economic instability, equipment failure or for any other reason, would limit our capacity to meet customer demands and delay new product development until a replacement facility and equipment, if necessary, were found. To date, such events have not had a material adverse effect on our business. However, such an event could disrupt our operations, forgo revenue opportunities, potentially lose market share, result in us being unable to timely satisfy customer demand, expose us to claims by our customers, result in significant expense to repair or replace our affected facilities, and, in some instances, could significantly curtail our research and development efforts in a particular product area or target market, any of which could materially and adversely affect our business. This disruption could also prevent our customers from resuming their own manufacturing following such an event, they may cancel or scale back their orders from us and this may in turn adversely affect our results of operations. Such events could also result in increased fixed costs relative to the revenue we generate and adversely affect our results of operations.
> >
> > [2] match 0.39 | later filing, paragraph 114 of 222
> A prolonged disruption of our or our suppliers' manufacturing facilities, research and development facilities, warehouses or other significant operations could have a material adverse effect on our business, financial condition and results of operations.
> >
> > [3] match 0.36 | later filing, paragraph 99 of 222
> Our semiconductor customers are not generally required to purchase specific quantities of products. Even when customers agree to source an agreed portion of their product needs from us, such arrangements often include pricing schedules or methodologies that apply regardless of the volume of products purchased, and those customers may not purchase the amount of product we expect. As a result, we may not generate the amount of revenue or achieve the level of profitability we expect under such arrangements. Moreover, our top customers' purchasing power has, in some cases, given them the ability to make greater demands on us with regard to pricing and contractual terms in general. Some customers may even reduce the amount of products or decline to purchase due to their internal development of the products. The loss of, or any substantial reduction in sales to, any of our top customers, including our hyperscale customers, could have a material adverse effect on our business, financial condition, results of operations and cash flows.

**Final label:** ____________  **Reason:** ____________

---

### R34 · NVDA_FY2025-u029

| | label | conf | reason |
|---|---|---|---|
| Claude | `boilerplate` | 2 | Competitive actions still covered by the competitor actions bullet. |
| ChatGPT | `material_modified` | 2 | The later text drops competitive actions from the scope of competitive-product risk. |

Position: earlier filing paragraph 59 of 197; later filing paragraph 59 of 209

**CONTEXT ONLY - paragraph before (unchanged)**

> •new or unexpected end-use cases;

**LABEL THIS - EARLIER TEXT (removed or changed)**

> •increase in demand for competitive products, including competitive actions;

**LABEL THIS - LATER TEXT (added or changed)**

> •increase in demand for competitive products;

**CONTEXT ONLY - paragraph after (unchanged)**

> •purchasing decisions made, and inventory levels held by, distributors, ODMs, OEMs, system integrators, other channel partners and other third parties;

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.55 | later filing, paragraph 52 of 209
> •competing technologies and competitor product releases, announcements or other actions;
> >
> > [2] match 0.53 | later filing, paragraph 100 of 209
> •decrease in demand for our products, services and technologies and those of our customers, partners or licensees;
> >
> > [3] match 0.51 | later filing, paragraph 175 of 209
> The AI Diffusion IFR would reduce the market for U.S.-designed and manufactured computing products and services, by expressly limiting exports, reexports, and transfers of covered products to Tier 2 countries and companies in Tier 1 countries that are either headquartered in Tier 2, or have an ultimate parent headquartered in a Tier 2 country. These restrictions would apply to all covered products, including products sold years ago.

**CONTEXT ONLY - where the LATER TEXT may come from in the earlier filing (top 3)**

> [1] match 0.65 | earlier filing, paragraph 63 of 197
> •the demand for our products; or
> >
> > [2] match 0.49 | earlier filing, paragraph 52 of 197
> •competing technologies and competitor product releases and announcements;
> >
> > [3] match 0.46 | earlier filing, paragraph 57 of 197
> •new product introductions and transitions resulting in less demand for existing products;

**Final label:** ____________  **Reason:** ____________

---

### R42 · AVGO_FY2024-u199

| | label | conf | reason |
|---|---|---|---|
| Claude | `material_modified` | 2 | Exposure: hedging statement and resulting FX losses dropped while FX risk remains. |
| ChatGPT | `material_removed` | 3 | The hedging and foreign-exchange-loss risk is not disclosed elsewhere in the later filing. |

Position: earlier filing paragraph 234 of 292

**CONTEXT ONLY - paragraph before (unchanged)**

> We operate global businesses and our consolidated financial results are reported in U.S. dollars. However, some of the revenue and expenses of our foreign subsidiaries are denominated in local currencies. Fluctuations in foreign exchange rates against the U.S. dollar could result in substantial changes in reported revenues and operating results due to the foreign exchange impact of remeasuring these transactions into U.S. dollars.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> In the normal course of business, we employ various hedging strategies to partially mitigate these risks, including the use of derivative instruments. These strategies may not be effective in protecting us against the effects of fluctuations in foreign exchange rates. As a result, fluctuations in foreign exchange rates could result in financial losses.

**LABEL THIS - LATER TEXT (added or changed)**

> (none: text removed)

**CONTEXT ONLY - paragraph after (unchanged)**

> We have potential tax liabilities as a result of VMware's former controlling ownership by Dell, which could have an adverse effect on our financial condition and operating results.

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.38 | later filing, paragraph 49 of 222
> Our business is subject to various domestic and international laws and other legal requirements, including anti-competition and import/export regulations, such as the U.S. Export Administration Regulations, and applicable executive orders. These laws, regulations and orders are complex, may change frequently and with limited notice, and generally become more stringent over time. We may be required to incur significant expense to comply with, or to remedy violations of, these regulations. In addition, if our customers fail to comply with these regulations, we may be required to suspend sales to these customers, which could damage our reputation and negatively impact our results of operations. The U.S. government may continue to add companies to its restricted entity list and/or technologies to its list of prohibited exports to specific countries, which have had and may in the future have an adverse effect on our revenue and our ability to sell our products. These restrictive governmental actions and any similar measures that may be imposed on U.S. companies by other governments, especially in light of ongoing trade tensions with China, will likely limit or prevent us from doing business with certain of our customers or suppliers and harm our ability to compete effectively or otherwise negatively affect our ability to sell our products. Furthermore, government authorities may take retaliatory actions, impose conditions for the supply of products or require the license or other transfer of IP, which could have a material adverse effect on our business.
> >
> > [2] match 0.38 | later filing, paragraph 175 of 222
> From time to time, we pursue litigation to assert our IP rights, including, in some cases, against our customers and suppliers. Claims of this sort could also harm our relationships with our customers and might deter future customers from doing business with us. Conversely, third parties have and may in the future pursue IP litigation against us, including as a result of our IP licensing business. Any inability to adequately protect our IP could limit the value of our technology, result in the loss of opportunities to sell or license our technology to others or limit our collection of royalty payments, any of which could negatively impact our business, financial condition and results of operations.
> >
> > [3] match 0.37 | later filing, paragraph 167 of 222
> The industries in which we operate are highly competitive and characterized by rapid technological changes, evolving industry standards, changes in customer requirements, often aggressive pricing practices and, in some cases, new delivery methods. We expect competition in these industries to continue to increase as existing competitors improve or expand their product offerings or as new competitors enter our markets. In addition, the trend toward consolidation is changing the competitive landscape. We expect this trend to continue, which may result in combined competitors having greater resources than us.

**Final label:** ____________  **Reason:** ____________

---

### R44 · AVGO_FY2024-u028

| | label | conf | reason |
|---|---|---|---|
| Claude | `boilerplate` | 2 | Summary bullet removed; FX risk still stated in the body. |
| ChatGPT | `material_removed` | 3 | The foreign-exchange-loss risk is not disclosed elsewhere in the later filing. |

Position: earlier filing paragraph 40 of 292

**CONTEXT ONLY - paragraph before (unchanged)**

> •The average selling prices of semiconductor products in our markets have often decreased rapidly and may do so in the future.

**LABEL THIS - EARLIER TEXT (removed or changed)**

> •Fluctuations in foreign exchange rates could result in losses.

**LABEL THIS - LATER TEXT (added or changed)**

> (none: text removed)

**CONTEXT ONLY - paragraph after (unchanged)**

> •We have potential tax liabilities as a result of VMware's former controlling ownership by Dell, which could have an adverse effect on our financial condition and operating results.

**CONTEXT ONLY - where the EARLIER TEXT may be in the later filing (top 3)**

> [1] match 0.50 | later filing, paragraph 29 of 222
> •Competition in our industries could prevent us from growing our revenue.
> >
> > [2] match 0.49 | later filing, paragraph 166 of 222
> Competition in our industries could prevent us from growing our revenue.
> >
> > [3] match 0.46 | later filing, paragraph 222 of 222
> Our Board of Directors has adopted a dividend policy pursuant to which we currently pay a cash dividend on our common stock on a quarterly basis. The declaration and payment of any dividend is subject to the approval of our Board of Directors and our dividend may be discontinued or reduced at any time. Because we are a holding company, our ability to pay cash dividends is also limited by restrictions or limitations on our ability to obtain sufficient funds through dividends from subsidiaries. There can be no assurance that we will declare cash dividends in the future in any particular amounts, or at all. A reduction in our cash dividend payments could have a negative effect on our stock price.

**Final label:** ____________  **Reason:** ____________

---
