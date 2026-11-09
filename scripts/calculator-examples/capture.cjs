// Capture the vendored CE X emulator, with a visible highlight on the last key.
// Run a development server first, then: node scripts/calculator-examples/capture.cjs
const {chromium}=require('playwright');
const {mkdir,writeFile}=require('node:fs/promises');
const path=require('node:path');
const examples=[
  {
    "id": "quadratic",
    "title": "Quadratic equations",
    "problem": "Solve x² − 3x + 2 = 0",
    "result": "The roots are x = 2 and x = 1. Substitution confirms that each makes the left side zero.",
    "steps": [
      [
        "MENU",
        "Open the mode menu with MENU."
      ],
      [
        "NEG",
        "Choose Equation/Func (A on this emulator)."
      ],
      [
        "2",
        "Choose 2: Polynomial."
      ],
      [
        "2",
        "Choose 2: Degree 2."
      ],
      [
        "1",
        "Enter the coefficient a = 1."
      ],
      [
        "EQ",
        "Confirm the first coefficient."
      ],
      [
        "NEG",
        "Press the negative key to enter b = −3."
      ],
      [
        "3",
        "Enter 3 after the negative sign."
      ],
      [
        "EQ",
        "Confirm b = −3."
      ],
      [
        "2",
        "Enter the constant c = 2."
      ],
      [
        "EQ",
        "Confirm c = 2."
      ],
      [
        "EQ",
        "Calculate the first root: x₁ = 2."
      ],
      [
        "EQ",
        "Move to the second root: x₂ = 1."
      ]
    ]
  },
  {
    "id": "table",
    "title": "Table of values",
    "problem": "Make a table for f(x) = x² at x = 0, 1 and 2",
    "result": "Plot the points (0,0), (1,1), and (2,4), and sketch the curve by hand.",
    "steps": [
      [
        "MENU",
        "Open the mode menu."
      ],
      [
        "9",
        "Choose Table."
      ],
      [
        "ALPHA",
        "Begin entering the variable x."
      ],
      [
        "RP",
        "Press the key labelled x."
      ],
      [
        "SQR",
        "Square x to enter x²."
      ],
      [
        "EQ",
        "Confirm f(x)."
      ],
      [
        "EQ",
        "Leave the second function blank and continue to the range."
      ],
      [
        "0",
        "Enter Start = 0."
      ],
      [
        "EQ",
        "Confirm the start value."
      ],
      [
        "2",
        "Enter End = 2."
      ],
      [
        "EQ",
        "Confirm the end value."
      ],
      [
        "1",
        "Enter Step = 1."
      ],
      [
        "EQ",
        "Confirm the step."
      ],
      [
        "EQ",
        "Create the table and read the x and f(x) pairs."
      ]
    ]
  },
  {
    "id": "linear",
    "title": "Linear equations with SOLVE",
    "problem": "Solve 2x + 3 = 7",
    "result": "The calculator gives x = 2. Check: 2 × 2 + 3 = 7.",
    "steps": [
      [
        "2",
        "Enter the coefficient 2."
      ],
      [
        "ALPHA",
        "Begin entering the variable x."
      ],
      [
        "RP",
        "Press the key labelled x."
      ],
      [
        "ADD",
        "Enter the plus sign."
      ],
      [
        "3",
        "Enter 3 on the left side."
      ],
      [
        "ALPHA",
        "Press ALPHA to enter an equality sign."
      ],
      [
        "CALC",
        "Press CALC for the equality sign printed above it."
      ],
      [
        "7",
        "Enter the right side, 7."
      ],
      [
        "SHIFT",
        "Begin SOLVE with SHIFT."
      ],
      [
        "CALC",
        "Press CALC to select SOLVE."
      ],
      [
        "0",
        "Enter an initial guess of 0."
      ],
      [
        "EQ",
        "Confirm the initial guess."
      ],
      [
        "EQ",
        "Display the solution x = 2."
      ]
    ]
  }
];
(async()=>{const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});try{for(const ex of examples){const page=await browser.newPage({viewport:{width:500,height:850},deviceScaleFactor:1});await page.goto(process.env.CALCULATOR_URL||'http://127.0.0.1:5173/vendor/fx991ce/src/index.html');await page.waitForSelector('[data-key="MENU"]');const dest=path.join('public/data/calculator-examples',ex.id);await mkdir(dest,{recursive:true});for(let i=0;i<ex.steps.length;i++){const [key]=ex.steps[i];await page.locator(`[data-key="${key}"]`).first().click();await page.evaluate(k=>{document.querySelectorAll('[data-key]').forEach(e=>{e.style.outline='';e.style.outlineOffset=''});let e=document.querySelector(`[data-key="${k}"]`);e.style.outline='4px solid #ff7900';e.style.outlineOffset='2px'},key);await page.locator('#calc').screenshot({path:path.join(dest,`${i+1}.png`),animations:'disabled'});}await page.close();console.log(ex.id,ex.steps.length)}await writeFile('public/data/calculator-examples/examples.json',JSON.stringify(examples,null,2)+'\n')}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
