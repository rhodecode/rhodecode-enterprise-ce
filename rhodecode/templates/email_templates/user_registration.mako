## -*- coding: utf-8 -*-
<%inherit file="base.mako"/>

<%def name="subject()" filter="n,trim">
RhodeCode new user registration
</%def>

## plain text version of the email. Empty by default
<%def name="body_plaintext()" filter="n,trim">

A new user `${user.username}` has registered on ${h.format_date(date)}

- Username: ${user.username}
- Full Name: ${user.firstname} ${user.lastname}
- Email: ${user.email}
- Profile link: ${h.url('user_profile', username=user.username, qualified=True)}
</%def>

## BODY GOES BELOW
<div style="white-space: pre-wrap">
${body_plaintext()}
</div>
