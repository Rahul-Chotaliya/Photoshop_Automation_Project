// photoshop_bridge.jsx

#target photoshop

var inputFile = new File(inputImagePath);
var outputFile = new File(outputImagePath);

if (!inputFile.exists) {
    alert("Input file not found: " + inputImagePath);
    exit();
}

app.open(inputFile);

// Optional: flatten layers, adjust resolution, etc.
// app.activeDocument.flatten();

// Save as JPG
var jpgSaveOptions = new JPEGSaveOptions();
jpgSaveOptions.quality = 12;
jpgSaveOptions.embedColorProfile = true;

app.activeDocument.saveAs(outputFile, jpgSaveOptions, true);
app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);


// // photoshop_bridge.jsx
// #target photoshop

// function placeLogoAndExport(inputImagePath, logoImagePath, x, y, outputPsdPath, outputJpgPath) {
//     try {
//         var doc = open(File(inputImagePath));

//         // Place Logo
//         var logo = File(logoImagePath);
//         app.open(logo);
//         var logoDoc = app.activeDocument;
//         logoDoc.selection.selectAll();
//         logoDoc.selection.copy();
//         logoDoc.close(SaveOptions.DONOTSAVECHANGES);

//         app.activeDocument = doc;
//         doc.paste();
//         var pastedLayer = doc.activeLayer;

//         // Position logo
//         pastedLayer.translate(x - pastedLayer.bounds[0], y - pastedLayer.bounds[1]);

//         // Export PSD
//         var psdFile = new File(outputPsdPath);
//         var psdOptions = new PhotoshopSaveOptions();
//         psdOptions.alphaChannels = true;
//         psdOptions.layers = true;
//         doc.saveAs(psdFile, psdOptions, true);

//         // Export JPG
//         var jpgFile = new File(outputJpgPath);
//         var jpgOptions = new JPEGSaveOptions();
//         jpgOptions.quality = 12;
//         doc.saveAs(jpgFile, jpgOptions, true);

//         doc.close(SaveOptions.DONOTSAVECHANGES);
//     } catch (e) {
//         alert("Error in JSX script: " + e.message);
//     }
// }
