## -*- coding: utf-8 -*-
<%inherit file="base.mako"/>

<%def name="subject()" filter="n,trim">
</%def>


## plain text version of the email. Empty by default
<%def name="body_plaintext()" filter="n,trim">
${body}
</%def>

## BODY GOES BELOW
<div style="white-space: pre-wrap">
${body_plaintext()}
</div>