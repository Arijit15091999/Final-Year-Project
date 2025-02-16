## Place the Firefox Driver in the System Path on Windows

### Step 1: Add `geckodriver.exe` to the System Path

1. Download `geckodriver.exe` from the [official GitHub releases page](https://github.com/mozilla/geckodriver/releases).
2. Extract the file and place `geckodriver.exe` in a directory (e.g., `C:\geckodriver`).
3. Add this directory to the system `PATH`:
   - Press `Win + R`, type `sysdm.cpl`, and press **Enter**.
   - Go to the **Advanced** tab and click **Environment Variables**.
   - Under **System Variables**, find `Path`, select it, and click **Edit**.
   - Click **New**, then add the path where `geckodriver.exe` is located (e.g., `C:\geckodriver`).
   - Click **OK** to save the changes.

### Step 2: Verify the Installation

Open **Command Prompt** and run:

```bash
geckodriver --version
```

If installed correctly, it should display the version of `geckodriver`.

### Step 3: Run the Commands

Once `geckodriver` is set up, navigate to your project directory and run:

```bash
pip install -r requirements.txt
python main.py


