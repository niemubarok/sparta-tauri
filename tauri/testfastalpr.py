from fast_alpr import ALPR
alpr = ALPR(detector_model="yolo-v9-t-384-license-plate-end2end", ocr_model="global-plates-mobile-vit-v2-model")
print(type(alpr))