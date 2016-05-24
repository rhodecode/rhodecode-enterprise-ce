// define module
var AgeModule = (function () {
  return {
    age: function(prevdate, now, show_short_version, show_suffix, short_format) {

  var prevdate =  moment(prevdate);
  var now = now || moment().utc();

  var show_short_version = show_short_version || false;
  var show_suffix = show_suffix || true;
  var short_format = short_format || false;

  // alias for backward compat
  var _ = function(s) {
    if (_TM.hasOwnProperty(s)) {
      return _TM[s];
    }
    return s
  };

  var ungettext = function (singular, plural, n) {
    if (n === 1){
      return _(singular)
    }
    return _(plural)
  };

  var _get_relative_delta = function(now, prevdate) {

    var duration = moment.duration(moment(now).diff(prevdate));
    return {
      'year': duration.years(),
      'month': duration.months(),
      'day': duration.days(),
      'hour': duration.hours(),
      'minute': duration.minutes(),
      'second': duration.seconds()
    };

  };

  var _is_leap_year = function(year){
    return ((year % 4 == 0) && (year % 100 != 0)) || (year % 400 == 0);
  };

  var get_month = function(prevdate) {
    return prevdate.getMonth()
  };

  var get_year = function(prevdate) {
    return prevdate.getYear()
  };

  var order = ['year', 'month', 'day', 'hour', 'minute', 'second'];
  var deltas = {};
  var future = false;

  if (prevdate > now) {
    var now_old = now;
    now = prevdate;
    prevdate = now_old;
    future = true;
  }
  if (future) {
    // ? remove microseconds, we don't have it in JS
  }

  // Get date parts deltas
  for (part in order) {
    var part = order[part];
    var rel_delta = _get_relative_delta(now, prevdate);
    deltas[part] = rel_delta[part]
  }

  //# Fix negative offsets (there is 1 second between 10:59:59 and 11:00:00,
  //# not 1 hour, -59 minutes and -59 seconds)
  var offsets = [[5, 60], [4, 60], [3, 24]];
  for (element in offsets) { //# seconds, minutes, hours
    var element = offsets[element];
    var num = element[0];
    var length = element[1];

    var part = order[num];
    var carry_part = order[num - 1];

    if (deltas[part] < 0){
        deltas[part] += length;
        deltas[carry_part] -= 1
    }

  }

  // # Same thing for days except that the increment depends on the (variable)
  // # number of days in the month
  var month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  if (deltas['day'] < 0) {
    if (get_month(prevdate) == 2 && _is_leap_year(get_year(prevdate))) {
      deltas['day'] += 29;
    } else {
      deltas['day'] += month_lengths[get_month(prevdate) - 1];
    }

    deltas['month'] -= 1
  }

  if (deltas['month'] < 0) {
    deltas['month'] += 12;
    deltas['year'] -= 1;
  }

  //# Format the result
  if (short_format) {
    var fmt_funcs = {
      'year': function(d) {return '{0}y'.format(d)},
      'month': function(d) {return '{0}m'.format(d)},
      'day': function(d) {return '{0}d'.format(d)},
      'hour': function(d) {return '{0}h'.format(d)},
      'minute': function(d) {return '{0}min'.format(d)},
      'second': function(d) {return '{0}sec'.format(d)}
    }

  } else {
    var fmt_funcs = {
      'year': function(d) {return ungettext('{0} year', '{0} years', d).format(d)},
      'month': function(d) {return ungettext('{0} month', '{0} months', d).format(d)},
      'day': function(d) {return ungettext('{0} day', '{0} days', d).format(d)},
      'hour': function(d) {return ungettext('{0} hour', '{0} hours', d).format(d)},
      'minute': function(d) {return ungettext('{0} min', '{0} min', d).format(d)},
      'second': function(d) {return ungettext('{0} sec', '{0} sec', d).format(d)}
    }

  }
  var i = 0;
  for (part in order){
    var part = order[part];
    var value = deltas[part];
    if (value !== 0) {

      if (i < 5) {
        var sub_part = order[i + 1];
        var sub_value = deltas[sub_part]
      } else {
        var sub_value = 0
      }
      if (sub_value == 0 || show_short_version) {
        var _val = fmt_funcs[part](value);
        if (future) {
          if (show_suffix) {
            return _('in {0}').format(_val)
          } else {
            return _val
          }

        }
        else {
          if (show_suffix) {
            return _('{0} ago').format(_val)
          } else {
            return _val
          }
        }
      }

      var val = fmt_funcs[part](value);
      var val_detail = fmt_funcs[sub_part](sub_value);
      if (short_format) {
        var datetime_tmpl = '{0}, {1}';
        if (show_suffix) {
          datetime_tmpl = _('{0}, {1} ago');
          if (future) {
            datetime_tmpl = _('in {0}, {1}');
          }
        }
      } else {
        var datetime_tmpl = _('{0} and {1}');
        if (show_suffix) {
          datetime_tmpl = _('{0} and {1} ago');
          if (future) {
            datetime_tmpl = _('in {0} and {1}')
          }
        }
      }

      return datetime_tmpl.format(val, val_detail)
    }
    i += 1;
  }

  return _('just now')

},
    createTimeComponent: function(dateTime, text) {
      return '<time class="timeago tooltip" title="{1}" datetime="{0}">{1}</time>'.format(dateTime, text);
    }
  }
})();


jQuery.timeago.settings.localeTitle = false;

// auto refresh the components every Ns
jQuery.timeago.settings.refreshMillis = templateContext.timeago.refresh_time;

// Display original dates older than N days
jQuery.timeago.settings.cutoff = templateContext.timeago.cutoff_limit;
