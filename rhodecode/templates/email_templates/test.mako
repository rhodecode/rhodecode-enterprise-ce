## -*- coding: utf-8 -*-
<%inherit file="base.mako"/>

<%def name="subject()" filter="n,trim">
Test "Subject" ${_('hello "world"')|n}
</%def>

<%def name="headers()" filter="n,trim">
X=Y
</%def>

## plain text version of the email. Empty by default
<%def name="body_plaintext()" filter="n,trim">
Email Plaintext Body
</%def>

## BODY GOES BELOW
<b>Email Body</b>

${h.short_id('0' * 40)}
${_('Translation')}