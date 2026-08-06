# Calendar Bookings

A single-owner appointment booking app: the Owner publishes Event Types, and Guests book Slots without accounts. There is no registration or authentication in the domain.

## Language

**Owner** (ru: «владелец календаря»):
The single, predefined person whose calendar is being booked. There is exactly one Owner; the admin area acts as this profile by default. Days and Business Hours are reckoned in the Owner's fixed timezone.
_Avoid_: admin, user, host, account

**Guest** (ru: «гость»):
An anonymous visitor who books a Slot. Guests have no account and no login.
_Avoid_: user, customer, invitee

**Event Type** (ru: «тип события», «вид брони»):
A named kind of appointment defined by the Owner: an owner-provided slug id, name, description, and duration in minutes (1–540; it must fit within a single Business Hours day). Event Types cannot be edited or deleted.
_Avoid_: booking kind, meeting type, event

**Slot** (ru: «слот»):
A time interval inside Business Hours that a Guest can book for a chosen Event Type; its duration equals that Event Type's duration. Starts lie on a grid anchored at 09:00, stepping by the Event Type's duration, and a Slot must fit entirely within Business Hours. A Slot is either free or occupied.
_Avoid_: time slot, availability

**Booking** (ru: «бронирование», «запись», «встреча»):
A Guest's reservation of one Slot for one Event Type, holding the Guest's name, email and optional comment. No two Bookings may overlap in time, regardless of Event Type. Bookings cannot be cancelled or rescheduled.
_Avoid_: meeting, appointment, reservation

**Booking Window** (ru: «окно записи»):
The calendar days on which Slots are offered: the current day plus the next 13, in the Owner's timezone. Slots in the past are never offered.
_Avoid_: availability window, schedule

**Business Hours** (ru: «рабочие часы»):
The fixed daily interval, 09:00–18:00 in the Owner's timezone, inside which Slots are generated. Not configurable by the Owner.
_Avoid_: availability, schedule, working day
