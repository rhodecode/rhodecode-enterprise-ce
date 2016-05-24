import logging
import datetime

from sqlalchemy import *
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import relation, backref, class_mapper, joinedload
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import declarative_base

from rhodecode.lib.dbmigrate.migrate import *
from rhodecode.lib.dbmigrate.migrate.changeset import *
from rhodecode.lib.utils2 import str2bool

from rhodecode.model.meta import Base
from rhodecode.model import meta
from rhodecode.lib.dbmigrate.versions import _reset_base, notify

log = logging.getLogger(__name__)


def get_by_name(cls, key):
    return cls.query().filter(cls.app_settings_name == key).scalar()


def get_by_name_or_create(cls, key, val='', type='unicode'):
    res = get_by_name(cls, key)
    if not res:
        res = cls(key, val, type)
    return res


def upgrade(migrate_engine):
    """
    Upgrade operations go here.
    Don't create your own engine; bind migrate_engine to your metadata
    """
    _reset_base(migrate_engine)
    from rhodecode.lib.dbmigrate.schema import db_2_3_0_0

    # issue fixups
    fixups(db_2_3_0_0, meta.Session)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine


def fixups(models, _SESSION):
    notify('Fixing existing GA code into new format')
    cur_code = get_by_name(models.RhodeCodeSetting, 'ga_code')
    val = '''
<script>
 // google analytics
 var _gaq_code = '_GACODE_';
 var _gaq = _gaq || [];
 _gaq.push(['_setAccount', _gaq_code]);
 _gaq.push(['_trackPageview']);

 (function() {
  var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
  ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
  var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
 })();

 rhodecode_statechange_callback = function(url, data){
  // ANALYTICS callback on html5 history state changed
  // triggered by file browser, url is the new url,
  // data is extra info passed from the State object
  if ( typeof window._gaq !== 'undefined' ) {
    _gaq.push(['_trackPageview', url]);
  }
 }
</script>'''
    if cur_code and getattr(cur_code, 'app_settings_value', ''):
        cur_val = getattr(cur_code, 'app_settings_value', '')
        val = val.replace('_GACODE_', cur_val)
        notify('Found GA code %s, migrating' % cur_val)
        new = get_by_name_or_create(models.RhodeCodeSetting, 'pre_code', val)
        new.app_settings_value = val
        _SESSION().add(new)
        _SESSION().commit()
