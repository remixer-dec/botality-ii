const t=["david","forsen","juice-wrld","obiwan","trump","xqc"].map(e=>({voice:e,model:`${e}.pth`,author:"enlyth",repo:"enlyth/baj-tts",path:"models/",size:.9,rename:!1,language:"en"})),l=["adam_carolla_checkpoint_1360000","alex_jones_checkpoint_2490000","david_attenborough_checkpoint_2020000","james_earl_jones_checkpoint_1600000","joel_osteen_checkpoint_2550000","neil_degrasse_tyson_checkpoint_1910000","tim_dillon_checkpoint_1970000","vincent_price_checkpoint_2080000"].map(e=>({voice:e.split("_checkpoint")[0],model:`${e}.pth`,author:"youmebangbang",repo:"youmebangbang/vits_tts_models",path:"",size:.9,rename:!0,language:"en"})),n=["G_20000","G_157","G_480","G_449","G_50000","G_18500.pth"],s=["Biden20k","BillClinton","BorisJohnson","GeorgeBush","Obama50k","Trump18.5k"].map((e,o)=>({voice:e.replace(/[0-9.]+k/,""),model:`${n[o]}.pth`,author:"Nardicality",repo:"Nardicality/so-vits-svc-4.0-models",path:`${e}/`,size:.5})),_=["G_50000","G_100000","G_85000"],r=["Glados_50k","Star-Trek-Computer","Boss_MGS_80k"].map((e,o)=>({voice:e.replace(/_[0-9]+k|-/g,""),model:`${_[o]}.pth`,author:"Amo",repo:"Amo/so-vits-svc-4.0_GA",path:`ModelsFolder/${e}/`,size:.5})),c=[{voice:"Tim_Cook",model:"Tim_Cook.pth",author:"Sucial",repo:"Sucial/so-vits-svc4.1-Tim_Cook",path:"",size:.2}],a=["2_K","3_K_L","3_K_M","3_K_S","4_0","4_K_M","4_K_S","5_0","5_K_M","5_K_S","6_K","8_0"],i=[["TheBloke/llama2_7b_chat_uncensored-GGUF","llama2_7b_chat_uncensored.Q$.gguf",a],["TheBloke/Luna-AI-Llama2-Uncensored-GGUF","luna-ai-llama2-uncensored.Q$.gguf",a],["TheBloke/Mistral-7B-Instruct-v0.1-GGUF","mistral-7b-instruct-v0.1.Q$.gguf",a],["TheBloke/WizardLM-1.0-Uncensored-Llama2-13B-GGUF","wizardlm-1.0-uncensored-llama2-13b.Q$.gguf",a],["TheBloke/Speechless-Llama2-Hermes-Orca-Platypus-WizardLM-13B-GGUF","speechless-llama2-hermes-orca-platypus-wizardlm-13b.Q$.gguf",a],["TheBloke/OpenBuddy-Llama2-13B-v11.1-GGUF","openbuddy-llama2-13b-v11.1.Q$.gguf",a],["TheBloke/TinyLlama-1.1B-Chat-v0.3-GGUF","tinyllama-1.1b-chat-v0.3.Q$.gguf",a]].map(e=>({name:e[1].split(".")[0],repo:e[0],model:e[1],quants:e[2],author:"TheBloke",path:"",size:"2-14"})),m={TTS:{VITS:[...t,...l],SO_VITS_SVC:[...s,...r,...c]},LLM:{GGUF:[...i]}};export{m as models};