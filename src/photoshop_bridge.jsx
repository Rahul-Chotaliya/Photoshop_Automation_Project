// photoshop_bridge.jsx

#target photoshop

// Expected global vars (injected via -r):
// inputImagePath, outputImagePath (legacy/simple flow)
// OR full placement flow:
// inputImagePath, logoImagePath, placeX, placeY, targetLogoWidth, outputPsdPath, outputJpgPath

function openDocument(path) {
    var f = new File(path);
    if (!f.exists) {
        throw new Error("File not found: " + path);
    }
    return app.open(f);
}

function saveAsJpg(doc, outPath) {
    var jpgFile = new File(outPath);
    var jpgOptions = new JPEGSaveOptions();
    jpgOptions.quality = 12;
    jpgOptions.embedColorProfile = true;
    doc.saveAs(jpgFile, jpgOptions, true);
}

function saveAsPsd(doc, outPath) {
    var psdFile = new File(outPath);
    var psdOptions = new PhotoshopSaveOptions();
    psdOptions.layers = true;
    psdOptions.alphaChannels = true;
    doc.saveAs(psdFile, psdOptions, true);
}

function placeAndScaleLogo(doc, logoPath, x, y, targetWidthPx) {
    // Place the logo as a smart object
    var logoFile = new File(logoPath);
    if (!logoFile.exists) {
        throw new Error("Logo file not found: " + logoPath);
    }

    app.activeDocument = doc;
    var idPlc = stringIDToTypeID("placeEvent");
    var desc = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    desc.putPath(idnull, logoFile);
    var idFreeTransformCenterState = stringIDToTypeID("freeTransformCenterState");
    var idQuadCenterState = stringIDToTypeID("quadCenterState");
    var idQcsAverage = stringIDToTypeID("QCSAverage");
    desc.putEnumerated(idFreeTransformCenterState, idQuadCenterState, idQcsAverage);
    var idOffset = stringIDToTypeID("offset");
    var offsetDesc = new ActionDescriptor();
    offsetDesc.putUnitDouble(charIDToTypeID('Hrzn'), charIDToTypeID('#Pxl'), x);
    offsetDesc.putUnitDouble(charIDToTypeID('Vrtc'), charIDToTypeID('#Pxl'), y);
    desc.putObject(idOffset, idOffset, offsetDesc);
    executeAction(idPlc, desc, DialogModes.NO);

    var layer = doc.activeLayer;

    // Compute current width and scale to targetWidthPx
    var b = layer.bounds; // [left, top, right, bottom]
    var currentWidth = b[2].as('px') - b[0].as('px');
    if (currentWidth <= 0) {
        return layer;
    }
    var scalePercent = (targetWidthPx / currentWidth) * 100.0;

    // Scale from center
    var idTrnf = charIDToTypeID("Trnf");
    var desc2 = new ActionDescriptor();
    var idnull2 = charIDToTypeID("null");
    var ref = new ActionReference();
    ref.putEnumerated(charIDToTypeID("Lyr " ), charIDToTypeID("Ordn"), charIDToTypeID("Trgt"));
    desc2.putReference(idnull2, ref);
    var idFTcs = charIDToTypeID("FTcs");
    var idQCSt = charIDToTypeID("QCSt");
    var idQcsa = charIDToTypeID("Qcsa");
    desc2.putEnumerated(idFTcs, idQCSt, idQcsa);
    var idScl = charIDToTypeID("Scl ");
    desc2.putUnitDouble(idScl, charIDToTypeID('#Prc'), scalePercent);
    var idSclY = stringIDToTypeID("scaleVertical");
    desc2.putUnitDouble(idSclY, charIDToTypeID('#Prc'), scalePercent);
    executeAction(idTrnf, desc2, DialogModes.NO);

    return layer;
}

try {
    // If full placement params exist, use them; else fallback to simple open-save
    if (typeof logoImagePath !== 'undefined' && typeof placeX !== 'undefined') {
        var doc = openDocument(inputImagePath);
        placeAndScaleLogo(doc, logoImagePath, placeX, placeY, targetLogoWidth);
        if (typeof outputPsdPath !== 'undefined') {
            saveAsPsd(doc, outputPsdPath);
        }
        if (typeof outputJpgPath !== 'undefined') {
            saveAsJpg(doc, outputJpgPath);
        }
        doc.close(SaveOptions.DONOTSAVECHANGES);
    } else {
        // Simple flow: open and save JPG
        var inputFile = new File(inputImagePath);
        var outputFile = new File(outputImagePath);
        if (!inputFile.exists) {
            throw new Error("Input file not found: " + inputImagePath);
        }
        var simpleDoc = open(inputFile);
        saveAsJpg(simpleDoc, outputFile.fsName);
        simpleDoc.close(SaveOptions.DONOTSAVECHANGES);
    }
} catch (e) {
    alert("JSX Error: " + e.message);
}
