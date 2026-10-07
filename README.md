# 🏰 VillagerAgent: A Graph-Based Multi-Agent Framework for Coordinating Complex Task Dependencies in Minecraft 🌍

<img src="img/VillagerBench.png" width="100%" /> 

<!-- <style>
.showcase-table {
    width: 100%;
    border-spacing: 10px;
    border-collapse: separate;
}

.showcase-cell {
    width: 25%;
    padding: 10px;
    background: #f5f5f5;
    border-radius: 8px;
    transition: transform 0.2s;
}

.showcase-cell:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.showcase-image {
    width: 256px;
    height: 256px;
    object-fit: cover;
    border-radius: 4px;
    margin-bottom: 8px;
}

.showcase-title {
    font-size: 14px;
    color: #333;
    margin-top: 8px;
    font-weight: 500;
}
</style> -->

<table class="showcase-table">
    <tr>
        <td class="showcase-cell" align="center">
            <img src="img/fishing.png" class="showcase-image" /><br>
            <sub class="showcase-title">Fishing</sub>
        </td>
        <td class="showcase-cell" align="center">
            <img src="img/build.png" class="showcase-image" /><br>
            <sub class="showcase-title">Building</sub>
        </td>
        <td class="showcase-cell" align="center">
            <img src="img/cart.png" class="showcase-image" /><br>
            <sub class="showcase-title">Driving</sub>
        </td>
        <td class="showcase-cell" align="center">
            <img src="img/conversition.png" class="showcase-image" /><br>
            <sub class="showcase-title">Talking</sub>
        </td>
    </tr>
    <tr>
        <td class="showcase-cell" align="center">
            <img src="img/farm.png" class="showcase-image" /><br>
            <sub class="showcase-title">Farming</sub>
        </td>
        <td class="showcase-cell" align="center">
            <img src="img/feed.png" class="showcase-image" /><br>
            <sub class="showcase-title">Feeding</sub>
        </td>
        <td class="showcase-cell" align="center">
            <img src="img/grow.png" class="showcase-image" /><br>
            <sub class="showcase-title">Cultivate</sub>
        </td>
        <td class="showcase-cell" align="center">
            <img src="img/saddle.png" class="showcase-image" /><br>
            <sub class="showcase-title">Holding</sub>
        </td>
    </tr>
    <tr>
        <td class="showcase-cell" align="center">
            <img src="img/ride.png" class="showcase-image" /><br>
            <sub class="showcase-title">Riding</sub>
        </td>
        <td class="showcase-cell" align="center">
            <img src="img/seed.png" class="showcase-image" /><br>
            <sub class="showcase-title">Seeding</sub>
        </td>
        <td class="showcase-cell" align="center">
            <img src="img/store.png" class="showcase-image" /><br>
            <sub class="showcase-title">Storing</sub>
        </td>
        <td class="showcase-cell" align="center">
            <img src="img/sleep.png" class="showcase-image" /><br>
            <sub class="showcase-title">Sleeping</sub>
        </td>
    </tr>
</table>


We aim to investigate the interactions between agents within the Minecraft environment and their collaboration with human players. Concurrently, we will explore the capabilities of Large Language Models (LLMs) in task decomposition and cooperation.

Welcome to VillagerBench, where the blocky world of Minecraft isn't just for fun and games—it's a testing ground for the cutting-edge of multi-agent collaboration! 🤖 Our benchmark suite is designed to push the boundaries of what virtual agents can achieve together, tackling everything from construction projects 🏗️ to culinary quests 🍳 and escape room puzzles 🔐.

Customize your private tasks in your Minecraft server with our VillagerAgent multi-agent framework, designed for personalized gameplay experiences! 🌟 
点击此处查看 [中文版 README](READMEzh.md)。
クリックして [README](README.md) をご覧ください。
<p align="center">
    <a href='https://arxiv.org/abs/2406.05720'>
      <img src='https://img.shields.io/badge/Paper-PDF-green?style=for-the-badge&logo=arXiv&logoColor=green' alt='Paper PDF'>
    </a>
    <a href='https://cnsdqd-dyb.github.io/workshare/2024/04/01/VillagerAgent.html'>
      <img src='https://img.shields.io/badge/Project-Page-blue?style=for-the-badge&logo=Web&logoColor=white' alt='Project Page'>
    </a>
</p>

---

## News

\[2026.10.07\] Added a sourced overview of research using VillagerBench and VillagerAgent: MultiAgentBench, CausalMACE, and Gated Coordination. See [Research adoption](#research-using-villagerbench-and-villageragent).

\[2024.12.18\] We've added new attributes. VillagerBaseAgent LLM 8b v1 will be released soon.

\[2024.12.11\] Support LLM api ranking with PPO method.

\[2024.12.08\] LLM driven AutoGen task to get data for Agent-tuning.

<table> <tr> <td><img src="img/chat.png" width="100%" /></td> <td><img src="img/chat2.png" width="100%" /></td> </tr> <tr> <td><img src="img/chat3.png" width="100%" /></td> <td><img src="img/chat4.png" width="100%" /></td> </tr> </table>

\[2024.12.01\] \[Human -- Agent\]  \[Agent -- Agent\] Real Time Chat supports now!!!🎉

<table> <tr> <td><img src="img/autogen1.png" width="100%" /></td> <td><img src="img/autogen2.png" width="100%" /></td> </tr>  </table> 

\[2024.10.23\] We are trying to replace the LLM in VillagerAgent with finetuned open source LLMs to improve the performance and efficiency of the agent's task execution.

\[2024.10.04\] 🎉Our minecraft multi-agent framework VillagerAgent has been accepted by ACL 2024.
## Research using VillagerBench and VillagerAgent

Last checked: **October 7, 2026**. VillagerBench tasks and the VillagerAgent framework support research on benchmark design, causal planning, and selective communication.

| Work | Publication | Verified use |
|---|---|---|
| [MultiAgentBench / MARBLE](https://aclanthology.org/2025.acl-long.421/) | ACL 2025 | Adapts our Minecraft environment and 11 building tools; reuses the same **100 target structures**. [Code](https://github.com/ulab-uiuc/MARBLE) |
| [CausalMACE](https://aclanthology.org/2025.findings-emnlp.777/) | EMNLP 2025 | Evaluates causal multi-agent planning on our **construction, cooking, and escape-room tasks**, following VillagerBench settings and metrics. |
| [Gated Coordination](https://arxiv.org/abs/2604.18975) | arXiv, April 2026 | Integrates gated communication into VillagerAgent; evaluates native construction tasks and a custom collaboration split preserving blueprint families. |

### Baseline comparisons and related research

[DeMAC](https://aclanthology.org/2025.findings-emnlp.757/) (EMNLP 2025) compares against VillagerAgent in Overcooked (Table 1). [PillagerBench](https://arxiv.org/abs/2509.06235) (IEEE CoG 2025) and [TickingCollabBench](https://arxiv.org/abs/2606.15684) (arXiv, June 2026) discuss our work in the context of competitive teams and time-sensitive collaboration. These relationships are listed separately from confirmed task reuse and framework integration.

See the [research evidence and source locations](doc/research_adoption.md). This is a curated list, not a complete citation count. To suggest an addition, open an issue with the paper/code link and the section explaining what was used.

## Setup and Configuration 🛠️

### Requirements
- **Python Version**: Python 3.8 or newer installed on your system.
- **API Keys**: Obtain API keys from one or more of the following services:
  - Alibaba Cloud Model Studio (for access to Qwen models)
  - OpenAI (for access to models like GPT-4)
  - Google Cloud (for access to models like Gemini)
  - Zhipu AI (for access to GLM models)
- **Node.js and npm**: Node Package Manager (npm) installed, which is typically included with Node.js.
- **Minecraft Server**: A Minecraft 1.19.2 server running locally or on a reachable host. For local quickstart, use `localhost:25565`. If you want to know how to configure the Minecraft 1.19.2 server, please see the [tutorial here](#minecraft-1192-server-setup).
- **Python Dependencies**: Install all necessary Python libraries as specified in the `requirements.txt` file. You can install these dependencies using the following command:
  ```
  pip install -r requirements.txt
  ```
- **Other Model Choice**: You have the option to use models from Hugging Face's Transformers library. Ensure you have the necessary credentials to use and download the model.

### Installation Steps
1. Clone the repository 📦:
   ```bash
   git clone https://github.com/cnsdqd-dyb/VillagerAgent-Minecraft-multiagent-framework.git
   cd VillagerAgent-Minecraft-multiagent-framework
   ```
2. Opt for a virtual environment 🧹:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, try venv\Scripts\activate
   ```
3. Install the dependencies 🧑‍🍳:
   ```bash
   pip install -r requirements.txt
   npm install
   python js_setup.py
   ```
4. Set up your API key 🗝️:
   - Craft a file named `API_KEY_LIST` and inscribe your API key in this way:
   ```json
   {
      "AGENT_KEY": ["put your qwen/dashscope api key here"]
   }
   ```
   - Place this file in the root of the project directory.

## QuickStart 🚀

1. Start a Minecraft 1.19.2 server and make sure it is reachable at `localhost:25565`.
2. Run the minimal example:
   ```bash
   python tiny_start.py
   ```
3. After `Alice` joins the server, grant it operator permission in the Minecraft server console:
   ```text
   /op Alice
   ```

The default model settings are defined near the top of `tiny_start.py`:

```python
LLM_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
LLM_API_MODEL = "qwen3-next-80b-a3b-instruct"
```

If your Minecraft server is not local, update `MINECRAFT_HOST` and `MINECRAFT_PORT` in `tiny_start.py`.

### Batch Testing 🧪
- Whip up test configs with `config.py` 📝.
- Kick off automated batch testing with `start_with_config.py` 🤖.


### Docker 🐳
- Build your Docker image with `docker build -t VillagerAgent .` 🏗.
- Launch the Docker container with `docker run VillagerAgent` 🚀.
- Note: If you need to open specific ports for API connectivity, you may need to modify the Dockerfile accordingly and launch with `docker run -p <your_port>:<app_port> VillagerAgent` 🌐.

## Overview 📜

### VillagerBench
Dive into VillagerBench, powered by Mineflayer, to explore the dynamics of cooperative AI. Our agents don't just play—they learn 🎓, adapt 🔄, and work together to overcome challenges that would stump the lone wolf 🐺.

<img src="img/benchmark.png" width="55%" /> 
<img src="img/radar.png" width="43.2%" /> 

### VillagerAgent Framework
Meet VillagerAgent, our multi-agent maestro 🎼, orchestrating a symphony of tasks with its four core components: Task Decomposer, Agent Controller, State Manager, and Base Agents. It's like a conductor for AI, turning individual actions into a masterpiece of collaboration.

<img src="img/framework.png" width="100%" /> 

## Core Components 🌟

- **VillagerBench**: The virtual sandbox where agents interact and learn 🤹.
- **TaskManager**: The master planner, keeping tasks on track and agents in the know 📊.
- **DataManager**: The keeper of knowledge, holding all the data cards close to its chest 🗃️.
- **GlobalController**: The overseer, ensuring every agent plays their part to perfection 🎯.


## npm Installation
### Windows

1. **Download the Node.js Installer**:
   - Visit the [Node.js official website](https://nodejs.org/).
   - Download the latest stable version of the Node.js installer for Windows (the LTS version is usually recommended).

2. **Run the Installer**:
   - Double-click the downloaded installer file.
   - Follow the instructions provided by the installation wizard. Make sure to include all necessary components, including npm, during the installation process.

3. **Verify Installation**:
   - Open Command Prompt or PowerShell.
   - Enter the following commands to check the versions of Node.js and npm:
     ```
     node -v
     npm -v
     ```
   - If the installation was successful, you will see the version numbers of Node.js and npm displayed.

### Linux (Debian/Ubuntu-based)

1. **Install Using Package Manager**:
   - Open the terminal.
   - First, update your package index:
     ```
     sudo apt update
     ```
   - Install Node.js and npm:
     ```
     sudo apt install nodejs npm
     ```

2. **Install Using nvm** (Node Version Manager, recommended for managing multiple versions of Node.js):
   - Open the terminal.
   - Install nvm by running:
     ```
     curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
     ```
   - Restart the terminal or run the following command to update the current session:
     ```
     export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
     [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm
     ```
   - Install Node.js using nvm (this will also install npm):
     ```
     nvm install node
     ```

3. **Verify Installation**:
   - Type the following commands to check the versions of Node.js and npm:
     ```
     node -v
     npm -v
     ```
   - If the installation was successful, you will see the version numbers of Node.js and npm displayed.


## Minecraft 1.19.2 Server Setup
### Preparation

1. **Ensure Java is Installed**: Minecraft servers require the Java runtime environment. Make sure you have the latest version of Java installed on your computer. You can check if Java is installed by running `java -version` in the command line.

2. **Download Server File**: Visit the official Minecraft website to download the 1.19.2 version of the server file (`minecraft_server.1.19.2.jar`).

### Configuring the Server

1. **Create a Server Folder**: Choose a location on your computer to create a new folder that will hold all the Minecraft server files.

2. **Move Server File**: Move the downloaded server file (`minecraft_server.1.19.2.jar`) into the folder you created.

3. **Run the Server**:
   - Open the command line interface.
   - Navigate to the folder containing the server file using the `cd` command.
   - Run the following command to start the server:
     ```
     java -Xmx1024M -Xms1024M -jar minecraft_server.1.19.2.jar nogui
     ```
   - The `-Xmx1024M` and `-Xms1024M` parameters set the maximum and initial memory allocation for the server in megabytes (MB). You may need to adjust these values based on your server's hardware.

4. **Accept the EULA**: The first time you run the server, a file named `eula.txt` will be generated. Open this file and change `eula=false` to `eula=true` to accept the Minecraft End User License Agreement.

5. **Restart the Server**: Run the `java` command again to start the server.

### Configuring Server Properties

1. **Edit the `server.properties` File**: After the first server run, a configuration file named `server.properties` will be generated. You can edit this file to customize the server settings, such as game mode, difficulty, etc. If you are testing the capabilities of multiple agents on VillagerBench, set the mode to peaceful and the terrain to superflat.

2. **Port Forwarding**: If you want other players to be able to access your server from outside networks, you may need to set up port forwarding on your router. By default, the Minecraft server uses port 25565.

3. **Start and Test the Server**: After completing all the settings, restart the server and try connecting to it to ensure everything is running smoothly.

### Important Notes

- Ensure that any agents that may join the server have been granted admin privileges (you can add permissions with the command `/op agent_name`).
- Make sure your server's firewall rules allow the port used by the Minecraft server.
- Regularly back up your server files to prevent data loss.
- Keep the server's Java version up to date for optimal performance and security.

The steps above provide a basic tutorial for setting up a Minecraft server. Depending on your specific needs and configuration, more advanced settings may be required.

## Citation
🌟 If you find our work helpful, please leave us a star and cite our paper.
```
@inproceedings{dong2024villageragent,
  title={VillagerAgent: A Graph-Based Multi-Agent Framework for Coordinating Complex Task Dependencies in Minecraft},
  author={Dong, Yubo and Zhu, Xukun and Pan, Zhengzhe and Zhu, Linchao and Yang, Yi},
  booktitle={Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (ACL)},
  year={2024},
  url={https://arxiv.org/abs/2406.05720}
}

```

## Contribution Guide 🤝

Jump on board! We love contributions. Before you submit your pull request, make sure:
- Your changes have aced the tests 🏆.
- You've spruced up the docs (if you've added some pizzazz) 📚.

## License 📜

This project is all yours under the [MIT License](LICENSE).
