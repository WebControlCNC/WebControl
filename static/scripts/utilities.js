/** parse the supplied value as a float and return it with 2 decimal places */
function dp2(value) {
  return parseFloat(value).toFixed(2)
}

function pwr2color(pwr) {
  var r, g, b = 0;

  if (pwr < 127) {
    g = 255;
    r = pwr * 2;
  }
  else {
    r = 255;
    g = 255 - (pwr - 127) * 2;
    if (pwr > 240) {
      g = 0
      b = (pwr - 240) * 16
    }
  }
  var h = r * 0x10000 + g * 0x100 + b * 0x1;
  return '#' + ('000000' + h.toString(16)).slice(-6);
}

export { dp2, pwr2color };