# Verified references used by the AquaEdge TRL-2 concept

Checked: 2026-08-30.

## Challenge / use case

1. TAQA Morocco Innovation Challenge — official 2026 site  
   https://waterchallenge.taqamorocco.ma/  
   Relevant points: rural-water focus; access, treatment/quality, management/valorization; digital solutions using sensors, data, AI and modelling are explicitly prioritized.

2. TAQA Morocco for Community — Water Challenge launch, 5 June 2026  
   https://www.taqamorocco.ma/fr/actualites-stories/taqa-morocco-community-lance-le-water-challenge

## Pilot-area evidence

3. *Integrated landscape analysis and multi-indicator assessment of groundwater drinking-water quality in marginal oasis environments: The case of Aguinane basin, Morocco*  
   Journal of African Earth Sciences, Volume 242, October 2026, 106253.  
   DOI: https://doi.org/10.1016/j.jafrearsci.2026.106253  
   Reported study scope: 18 wells in Aguinane Oasis; nitrate pollution identified in Tamsoult; microbiological contamination in Kiriout; high mineralization in Adkhess.

## Hardware / automation

4. Revolution Pi / RevPi Connect 5 documentation  
   https://revolutionpi.com/en/docs/revpi-connect-5  
   The reference architecture treats RevPi Connect 5 as the modular industrial base unit, not as a bare microcontroller board.

5. Raspberry Pi Compute Module 5  
   https://www.raspberrypi.com/products/compute-module-5/

## Model Hardware Standard

6. Anthropic — *Previewing the Model Hardware Standard*, 27 August 2026  
   https://www.anthropic.com/news/model-hardware-standard-research-preview  
   AquaEdge uses the wording **MHS-ready / MHS-inspired** and does not claim formal MHS compliance while the specification remains a research preview.

## Local/open models and APIs

7. Ollama API documentation  
   https://docs.ollama.com/api/introduction

8. Ollama — Gemma 3 4B  
   https://ollama.com/library/gemma3:4b  
   Used as a compact local benchmark candidate.

9. Ollama — GPT-OSS 20B / 120B  
   https://ollama.com/library/gpt-oss  
   Used as a higher-capability open-weight benchmark candidate where memory permits.

10. Qwen/Qwen3-4B-Instruct-2507 — Hugging Face model card  
    https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507  
    Apache-2.0; used as the default optional LoRA/QLoRA adaptation target in the repository.

11. Groq API docs / supported models  
    https://console.groq.com/docs/overview  
    https://console.groq.com/docs/models

12. Mistral API documentation / pricing  
    https://docs.mistral.ai/  
    https://docs.mistral.ai/inference/pricing

13. Claude API documentation  
    https://platform.claude.com/docs/en/get-started

14. OpenAI API — Responses API / Assistants migration  
    https://developers.openai.com/api/docs/assistants/migration  
    New integration code must use the Responses API rather than the sunset Assistants API.

15. Hugging Face Inference Providers  
    https://huggingface.co/docs/inference-providers/index

## Evidence policy

- The repository distinguishes **published/official sources**, **simulation assumptions**, and **future field measurements**.
- Synthetic ML metrics are not field measurements.
- Exact Tamsoult hydraulic topology, node distances, radio budget and sensor calibration remain to be established during field engineering.
