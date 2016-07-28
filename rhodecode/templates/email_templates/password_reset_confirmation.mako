## -*- coding: utf-8 -*-
<%inherit file="base.mako"/>

<%def name="subject()" filter="n,trim">
Your new RhodeCode password
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
Below is your new access password for RhodeCode.
<br/>
<strong>If you didn't request a new password, please contact your RhodeCode administrator.</strong>
</p>
<p>password: <input value='${new_password}'></pre></p>