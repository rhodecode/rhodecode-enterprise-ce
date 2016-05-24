## -*- coding: utf-8 -*-
<%inherit file="base.mako"/>

<%def name="subject()" filter="n,trim">
Your new RhodeCode password
</%def>

## plain text version of the email. Empty by default
<%def name="body_plaintext()" filter="n,trim">
Hi ${user.username},

Below is your new access password for RhodeCode.

password: ${new_password}

*If you didn't request a new password, please contact your RhodeCode administrator immediately.*
</%def>

## BODY GOES BELOW
<div style="white-space: pre-wrap">
${body_plaintext()}
</div>