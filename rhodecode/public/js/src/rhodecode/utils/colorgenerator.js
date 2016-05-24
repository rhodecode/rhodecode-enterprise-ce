// # Copyright (C) 2010-2016  RhodeCode GmbH
// #
// # This program is free software: you can redistribute it and/or modify
// # it under the terms of the GNU Affero General Public License, version 3
// # (only), as published by the Free Software Foundation.
// #
// # This program is distributed in the hope that it will be useful,
// # but WITHOUT ANY WARRANTY; without even the implied warranty of
// # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// # GNU General Public License for more details.
// #
// # You should have received a copy of the GNU Affero General Public License
// # along with this program.  If not, see <http://www.gnu.org/licenses/>.
// #
// # This program is dual-licensed. If you wish to learn more about the
// # RhodeCode Enterprise Edition, including its added features, Support services,
// # and proprietary license terms, please see https://rhodecode.com/licenses/

/**
* SmartColorGenerator
*
*usage::
*  var CG = new ColorGenerator();
*  var col = CG.getColor(key); //returns array of RGB
*  'rgb({0})'.format(col.join(',')
*
* @returns {ColorGenerator}
*/

// TODO: no usages found. Maybe it's time to remove it
var ColorGenerator = function(){
  this.GOLDEN_RATIO = 0.618033988749895;
  this.CURRENT_RATIO = 0.22717784590367374; // this can be random
  this.HSV_1 = 0.75;// saturation
  this.HSV_2 = 0.95;
  this.color;
  this.cacheColorMap = {};
};

ColorGenerator.prototype = {
  getColor:function(key){
    if(this.cacheColorMap[key] !== undefined){
      return this.cacheColorMap[key];
    }
    else{
      this.cacheColorMap[key] = this.generateColor();
      return this.cacheColorMap[key];
    }
  },
  _hsvToRgb:function(h,s,v){
    if (s === 0.0)
        return [v, v, v];
    i = parseInt(h * 6.0);
    f = (h * 6.0) - i;
    p = v * (1.0 - s);
    q = v * (1.0 - s * f);
    t = v * (1.0 - s * (1.0 - f));
    i = i % 6;
    if (i === 0)
        return [v, t, p];
    if (i === 1)
        return [q, v, p];
    if (i === 2)
        return [p, v, t];
    if (i === 3)
        return [p, q, v];
    if (i === 4)
        return [t, p, v];
    if (i === 5)
        return [v, p, q];
  },
  generateColor:function(){
    this.CURRENT_RATIO = this.CURRENT_RATIO+this.GOLDEN_RATIO;
    this.CURRENT_RATIO = this.CURRENT_RATIO %= 1;
    HSV_tuple = [this.CURRENT_RATIO, this.HSV_1, this.HSV_2];
    RGB_tuple = this._hsvToRgb(HSV_tuple[0],HSV_tuple[1],HSV_tuple[2]);
    function toRgb(v){
        return ""+parseInt(v*256);
    }
    return [toRgb(RGB_tuple[0]),toRgb(RGB_tuple[1]),toRgb(RGB_tuple[2])];

  }
};
