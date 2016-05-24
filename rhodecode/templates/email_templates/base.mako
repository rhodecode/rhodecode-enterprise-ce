## -*- coding: utf-8 -*-

## headers we additionally can set for email
<%def name="headers()" filter="n,trim"></%def>

## plain text version of the email. Empty by default
<%def name="body_plaintext()" filter="n,trim"></%def>

${self.body()}


<div>
--
<br/>
<br/>
<b>${_('This is a notification from RhodeCode. %(instance_url)s') % {'instance_url': instance_url}}</b>
</div>
