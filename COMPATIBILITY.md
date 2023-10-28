<table>
<thead>
  <tr>
    <th>Backend</th>
    <th>Model</th>
    <th>Features<br></th>
    <th>Acceleration<br></th>
    <th>Chronicler</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>pytorch</td>
    <td>llama_orig</td>
    <td>- adepter support<br>- visual input (multimodal adapter)<br><br></td>
    <td>CUDA<br>MPS<br></td>
    <td>instruct</td>
  </tr>
  <tr>
    <td>pytorch</td>
    <td>llama_hf</td>
    <td>- lora support<br><br></td>
    <td>CUDA</td>
    <td>instruct</td>
  </tr>
  <tr>
    <td>pytorch</td>
    <td>gpt-2, gpt-j, auto-model</td>
    <td></td>
    <td>CUDA</td>
    <td>instruct<br></td>
  </tr>
  <tr>
    <td>llama.cpp<br>remote-lcpp<br></td>
    <td>any llama-based<br></td>
    <td>- quantized GGML model support<br>- lora support<br>- built-in GPU acceleration<br>- memory manager support <br> - visual input (currently only in llama.cpp server)</td>
    <td>CPU<br>CUDA<br>Metal<br><br></td>
    <td>instruct</td>
  </tr>
  <tr>
    <td>mlc-pb</td>
    <td>only brebuilt in mlc-chat<br></td>
    <td>- quantized MLC model support<br></td>
    <td>CUDA<br>Vulkan<br>Metal</td>
    <td>raw</td>
  </tr>
  <tr>
    <td>remote_ob</td>
    <td>any supported by oobabooga webui and kobold.cpp<br></td>
    <td>- all features of Oobabooga webui, including GPTQ support that are available via API<br><br>- all features of Kobold.cpp that are available via API<br>- memory manager support</td>
    <td>+<br></td>
    <td>instruct</td>
  </tr>
</tbody>
</table>