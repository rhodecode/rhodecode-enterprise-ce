## -*- coding: utf-8 -*-
<%inherit file="base.mako"/>

<%def name="subject()" filter="n,trim">
</%def>


## plain text version of the email. Empty by default
<%def name="body_plaintext()" filter="n,trim">
${body}
</%def>

## BODY GOES BELOW
<table style="text-align:left;vertical-align:top;">
    <tr><td style="padding-right:20px;padding-top:15px;white-space:pre-wrap">${body}</td></tr>
</table>