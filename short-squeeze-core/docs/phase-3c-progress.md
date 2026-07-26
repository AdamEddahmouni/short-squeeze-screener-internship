# Phase 3C Progress

Phase 3C adds the isolated `squeeze_core.analysis` package, five explicit standard cohorts, outcome-blind boundary selection, exact proportions, deterministic Wilson intervals, sample-size and dependence assessments, descriptive confusion matrices and prevalence, missingness and registry quality, self-describing results, canonical serialization, Markdown reports, offline CLI commands, fixtures, 38 anchors, and compatibility/isolation guards.

The primary historical result contains one unique symbol and one earliest selected BIYA boundary. The case-boundary result contains two dependent BIYA observations. The synthetic result is software coverage only. The all-registered and partial/blocked reports retain incomplete and conflicted cases without fabricating evidence.

## Verification

Fresh-basetemp suites pass with analysis 120, research 65, evaluation 50, validation 367, readiness 124, metrics 453, and compatibility 130 tests. The complete suite passes with `1893 passed, 1 skipped in 108.77s`.

Two generator passes produced the same bytes for all 17 analysis fixture files. Each standard CLI analysis and Markdown report also matched across two independent runs:

| View | Analysis SHA-256 | Report SHA-256 |
| --- | --- | --- |
| Historical unique symbol | `4d1ecbd264dd50428a62275d75bd646d994b75d2e43a30368cb36b083bcd7c95` | `6e2fbf1f431de1ce83ff051ac37756af065f009445997c44c8f4bc07be724326` |
| Historical case boundary | `9d1d653e8db5caadab55218f4eb17fb6002f0fa85b2ac6960dd6388dc0801082` | `3e32ea9ea9d9f39c5094d1d943acec8ae1d64481013be340d5d4f3771c7a3f62` |
| Synthetic | `9d15b830a57100efd70b0ac3260ff4b828a88b74001cb6b5330cd68438a20e03` | `2f00af53f6d45f3f28ad8628e7b0e722fb2d19ecf1d9a2cd1e851c83ce2fa852` |
| All registered | `0cef83d36fe4cc527f368a079eea8f99e21f6b43ac205d7afa2545fb3995f13b` | `9612e10c79a16c62c90e29dcd3a16a4780efd20501007fb5ad7211e7b5249764` |
| Partial/blocked | `f09d942dfb0521135512a54a5155d9d561461882f3320c777d0665b4ea8f1983` | `dc459407148f9314dee401ddca5ed026c01e008a427fe6fb8c46bfa881e345e5` |

All nine Phase 1–3B manifests are unchanged from `e0708f51212ab11fd5767fc55b41b58f4614b44b`. Schema version remains `1.0.0`; no remote is configured. Archived repositories remain at `0897562e05d75b812dd284de81dfafdfa1dea916`, `6dbefd1a6b271bfc48106c4aa002f211735551cd`, and `84f770ddf33cf35bbe4ec3d8dfc12876d0068fd8`.

## Phase 3C anchor hashes

| Anchor | SHA-256 |
| --- | --- |
| `historical_case_boundary_cohort` | `b77b1272a54b92846050363a263f07de1c52889798b0f192bcbdf96b84e7318d` |
| `historical_unique_symbol_cohort` | `93c272824e113b496c8968095eb6702d9512e508aa8d6dabb628b3eff9f789a5` |
| `synthetic_case_cohort` | `9ec8f1d312a829881227825c728af5ccf754af3c1eba275aaf473b24e9f7351d` |
| `all_registered_case_cohort` | `861f85f927a855f37adab0d124d6cfd27bd2afec7f41a3be480d24ba76647f17` |
| `partial_blocked_case_cohort` | `2a30dfbbc17c7537002de60ce8e56d409b93ee48260e4449ee0ed2220f596405` |
| `earliest_boundary_selection` | `be13e2b8808d90e6ec3fb1a32515e9bba75d35877341abf742021bc806bb6db5` |
| `biya_symbol_dependence_summary` | `4a509b2aa1bde6b7a5b4ddcc6223ac27e9947a0ce4491b31a284ca765540aa6d` |
| `sample_size_zero` | `3f41c075bd9d517e60fabd9db3bc5e4fde4121c55430a668d2cd261fe76db474` |
| `sample_size_one` | `d7a1b3a44072fcc0272dd488e2b49e3688fb3e7ac89e309e247ae9ff117c5031` |
| `sample_size_very_small` | `b0958f3cfd8fa37000bb94cda1d6c403f3d2bc8d7258ec27b50b6bb37265a220` |
| `proportion_zero_of_one` | `ca390075712b4c612ca634c18f3d69d7aa9e7b0828c2bd476bd4330b18c0a91f` |
| `proportion_one_of_one` | `c45188361ada3d5612f3e43ef53ea32cea5aa58e008d9a6e33dd4270b9788280` |
| `proportion_one_of_two` | `fda105e6c108a6bdb112a36ffb62d45cb59d37377e1ae3fb7e6c3d77a7602eba` |
| `proportion_undefined` | `525dae785dc37a9571646f589eb0bc41cfc9086d80cc97bab2cc4413b985a80a` |
| `wilson_zero_success` | `40c4bc7806688fbd6cfda2780a136aa575b24def461da0345402e3eac7adc534` |
| `wilson_all_success` | `144c31d2186756c8adb5f7940024dcada0635606aaaf76cb92170d8600bb0ae5` |
| `wilson_one_of_two` | `b917a0066a2b725ff87165c58c91ff8c458c9f99431497a4267a822e8fd06a10` |
| `confusion_matrix_historical_case_boundary` | `b6c48b384d4b868c86d07c316e1724328600eb593cb6f1748fbefb46d435949b` |
| `confusion_matrix_historical_unique_symbol` | `d9f264fef9fc57c1d690a3affea82dc8421def5bd4d55ace4107193cfb219bdb` |
| `rule_prevalence_historical_case_boundary` | `21e1089ebabef80e311282ac9ab7df5da813de744520120f4c45e71ee63fc804` |
| `rule_prevalence_historical_unique_symbol` | `389837b07b1688bee9d486ba649d65aedf5644526c3879923d8b2792f89673d1` |
| `rule_prevalence_synthetic` | `a174aaed3f07d1867c2c36c110064748b62494d63d55802a841cb52b29d17aac` |
| `missingness_historical` | `cea064bdd6b2a7d428e648803545ac1945ed5a4b071c86af9a4839e04789f045` |
| `missingness_all_registered` | `196e8f297e1d6aede3c719c33958ef4a4ad37b7a82819ac50272307ca7687a32` |
| `detection_prevalence_historical` | `c0a1e1c74b43d908f9856f8b80c6d68f216af2f372c3c7294150521473b24cac` |
| `outcome_prevalence_historical` | `dc23220c726a8d9092b306033936b4106f6dd02c7316a502f8168acb51802de3` |
| `classification_prevalence_historical` | `6bf055d693350a45096765e65284b1dba4b91853a80af913ffeff710cd429f66` |
| `biya_case_boundary_analysis` | `2bcb35d23542e227815b9bd08c39183598eacb00b3e2d4c0b7cc59c5dea7b9d0` |
| `biya_unique_symbol_analysis` | `c1da79dc0c958e53ad074d6c0b90cfb4a709af3ecd5adddfd8d1f6edfe832ca7` |
| `historical_case_boundary_report` | `d49837cf1413261cc8ad73aa8d1dac3680af756b1cfd9b0ec5f92e0565f78555` |
| `historical_unique_symbol_report` | `775df9946a031408a22f18cccd7b17b6230f3a279e315f71051abf1bdebd527e` |
| `synthetic_report` | `f9ef43f1cb6849784fdda25e2c201a795de43daf237f949d2b9aaa9e1c1c1704` |
| `all_registered_data_quality_report` | `3d9bacc341f971faeb6040c85161b2b391f0118d8496d63152a22f1499060ec6` |
| `partial_blocked_report` | `ea08dd245f6762baaa0791ed5a122c8c120bbdbbca0c6d23d54d75fbf4a54485` |
| `phase_3c_cli_output` | `c1da79dc0c958e53ad074d6c0b90cfb4a709af3ecd5adddfd8d1f6edfe832ca7` |
| `phase_3c_report_cli_output` | `775df9946a031408a22f18cccd7b17b6230f3a279e315f71051abf1bdebd527e` |
| `mixed_phase_3c_output` | `866660880378a21e2cd26f9ada91c6dea358e940be021f6fe33f17a988f402dd` |
| `serialized_phase_3c_collection` | `ae046a40d1b34a04cf3a295bd622fab3154d5bfe4a2557a9e3da2e8eb07d10a3` |

## Additive Phase 3D note

Phase 3D was later added without modifying any Phase 3C anchor or fixture. Phase 3C remains the unchanged descriptive-analysis input boundary for any Phase 3D cases that eventually pass provenance, identity, eligibility, boundary-freeze, and leakage review.
