# Django_Hospital_Management


🏥 Django Hospital Management System – Appointment & Slot Booking API

A full-stack backend system built with Django, designed to manage hospital operations including doctor slot creation, patient appointment booking, appointment rescheduling, cancellation, JWT-based authentication, and automatic expired-slot cleanup.

This system provides a secure, scalable, and automated workflow for clinics, hospitals, and online consultation platforms.

🚀 Key Features
🧑‍⚕️ Doctor Module

Doctors can:

Create single slots or multiple slots across a date range

Prevent overlapping slots

Update slot details (date, time, duration, status)

Delete one or multiple slots

View the slots they created

View upcoming patient appointments

Automatically delete expired slots (Handled by middleware)

🧑‍🤝‍🧑 Patient Module

Patients can:

View available slots across a date range

Book appointments for future time slots

View all booked appointments

Cancel existing appointments

Reschedule appointments to another available slot

Prevent double booking or overlapping booking conditions

🔐 Authentication & Authorization

Custom JWT Middleware handles:

Extracting Bearer tokens

Validating JWT signatures

Auto-attaching:

request.patient

request.doctor

request.user

Blocking unauthorized access


🧠 Internal Workflows Explained
🔁 1. Slot Creation Logic

Uses:

start_date → end_date

start_time → end_time

slot_duration (minutes)

Auto-generates time slots using:

timedelta(minutes=slot_duration)


Prevents:

Overlapping new vs existing slots

Creating past slots

Invalid date/time formatting

🔁 2. Appointment Booking Workflow

Patients select a valid slot

System verifies:

Slot exists

Slot is "available"

Slot is in the future

On booking:

Appointment created

Slot status updated → not available

🔁 3. Appointment Cancellation

Status → cancelled

Slot is updated back to "available"

🔁 4. Rescheduling Logic

Ensures:

Old appointment exists

New slot is available

Updates both old and new slot statuses

Appointment status changes → rescheduled

🏗️ Tech Stack

Python

Django

Django ORM

JWT Authentication

MySQL / SQLite

Datetime & Timedelta Logic

📌 Outcome

This project represents a complete and production-ready backend system for modern hospitals or clinics.
It demonstrates your ability to build:

Complex scheduling systems

Secure authentication middleware

Role-based access control

Database-driven automated workflows

Real-world appointment logic
