# 💾 System Breach: Protocol | Design Documentation

## 🌌 Project Overview
**System Breach: Protocol** is a cyberpunk-themed brick-breaker where the player acts as a netrunner infiltrating the "Data Stream Core." Instead of breaking bricks, you are de-compiling encrypted modules to extract high-value intelligence.

---

## 🕹️ Core Gameplay Mechanics

### The Paddle (The Decoder)
The player controls a **High-Frequency Decryption Paddle**.
* **Function:** Reflects the Energy Sphere to prevent "Connection Loss" (dropping the ball).
* **Visuals:** Carbon-fiber chassis with neon cyan reactive lighting.

### The Ball (Energy Sphere)
The **Energy Sphere** is your primary probe.
* **Logic:** As it strikes modules, it sends a pulse that disrupts the data integrity of the block.
* **Visuals:** A glowing cyan ring with a high-velocity motion trail.

---

## 💎 Data Modules & Power-Ups
In this system, "Bricks" are categorized as **Data Modules**. Destroying specific modules releases **Subroutines** (Power-ups) that the player must catch.

### 1. Module Classifications
| Icon Type | Name | Hardness | Description |
| :--- | :--- | :--- | :--- |
| **Neon Green/Blue** | Raw Cache | 1 Hit | Standard data fragments. Common. |
| **Circuit Etched** | Hardened Firmware | 2-3 Hits | Encrypted modules requiring multiple impacts to crack. |
| **Red Warning** | Volatile Logic | 1 Hit | Triggering this causes a localized "Data Explosion" affecting nearby blocks. |

### 2. Active Subroutines (Power-Ups)
When a high-value module is destroyed, it may drop one of the following:

* **`MULTI-BALL` (Yellow Power Up Module):** Immediately forks the current process, splitting the Energy Sphere into three separate probes.
* **`SPEED_BOOST` (Blue Boost Module):** Overclocks the Sphere's velocity, increasing destruction power but requiring faster reflexes.
* **`HEALTH+` (Green Cross Module):** Restores a lost connection (Extra Life).
* **`OVERSIZE_BUFFER` (Circuit Module):** Temporarily extends the width of the Decryption Paddle.

---

## 💥 Visual Feedback & Effects

### Block Destruction
When a module's integrity reaches 0%, the following effects are triggered:
1.  **Ignition Phase:** A bright white flash at the point of impact.
2.  **Kinetic Fragments:** Large chunks of "hardware" fly off, spinning with gravity-based physics.
3.  **Digital Debris:** Tiny pixelated "code glitches" and sparkles that fade over 1 second to simulate data dissipation.

### Power-Up Synthesis
Collecting a falling module triggers a **Synthesis Phase**, where the paddle glows gold and a UI notification appears in the "Active Module" sidebar.

---

## 🖥️ Technical Specifications
* **Resolution:** 1280x720 (HD Widescreen)
* **Engine:** Pygame (CPU-based rendering)
* **Art Style:** 16-bit Cyberpunk Pixel Art
* **Aspect Ratio:** 16:9
