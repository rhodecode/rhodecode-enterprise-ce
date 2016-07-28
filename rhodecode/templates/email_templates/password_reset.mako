## -*- coding: utf-8 -*-
<%inherit file="base.mako"/>

<%def name="subject()" filter="n,trim">
RhodeCode Password reset
</%def>

## plain text version of the email. Empty by default
<%def name="body_plaintext()" filter="n,trim">
Hi ${user.username},

There was a request to reset your password using the email address ${email} on ${h.format_date(date)}

*If you didn't do this, please contact your RhodeCode administrator.*

You can continue, and generate new password by clicking following URL:
${password_reset_url}

${self.plaintext_footer()}
</%def>

## BODY GOES BELOW
<p>
Hello ${user.username},
</p><p>
There was a request to reset your password using the email address ${email} on ${h.format_date(date)}
<br/>
<strong>If you did not request a password reset, please contact your RhodeCode administrator.</strong>
</p><p>
${_('<a href="%(url)s">Generate new password here</a>.') % {'url': password_reset_url} |n}
</p>