<template>
  <LegalLayout title="Privacy Policy" :effective-date="info.privacyEffectiveDate">
    <p>
      {{ info.appName }} is an evacuation center management and hazard reporting system operated by the
      {{ info.office }} of {{ info.province }} ("PDRRMO", "we", "us"). This policy explains what personal
      information we collect, why we collect it, who we share it with, and the rights you have under the
      <strong>Data Privacy Act of 2012 (Republic Act No. 10173)</strong> and its Implementing Rules and Regulations.
    </p>
    <p>
      The PDRRMO is the Personal Information Controller for the data processed through {{ info.appName }}.
    </p>

    <h2>1. Information we collect</h2>

    <h3>a. When you create an account</h3>
    <ul>
      <li>First and last name</li>
      <li>Email address (verified with a one-time code)</li>
      <li>Contact number (optional)</li>
      <li>Municipality</li>
      <li>Password, which is stored only in hashed form; we cannot see it</li>
      <li>Account details such as your role, sign-up date and last login time</li>
    </ul>

    <h3>b. When you submit a hazard report</h3>
    <ul>
      <li>Hazard type, severity, title and description</li>
      <li>Location of the hazard: GPS coordinates and address</li>
      <li>Photos you upload</li>
      <li>The contact name and phone number you enter on the report</li>
    </ul>

    <h3>c. Your location</h3>
    <p>
      With your permission, your browser shares your device's location so we can show you on the map, suggest
      the nearest suitable evacuation center, plan routes, and alert you to nearby hazards. You can refuse or
      turn this off in your browser settings at any time; those features will then be limited. Your last known
      location may be kept in your browser's storage on your device. When you request a route, the starting
      point and destination (rounded to about one meter) are recorded in our system logs.
    </p>

    <h3>d. If you are registered at an evacuation center</h3>
    <p>
      Authorized evacuation center staff may record evacuee information: full name, age, sex, contact number,
      address, family head, and whether a person is a child, senior citizen, person with disability (PWD),
      pregnant or lactating. Some of this is <strong>sensitive personal information</strong> under the Data
      Privacy Act. We collect it only to provide relief, prioritize vulnerable evacuees, and produce the
      affected-population reports required in disaster response.
    </p>

    <h3>e. Information collected automatically</h3>
    <ul>
      <li>IP address, browser and device type (user agent)</li>
      <li>Actions taken in the system, such as logins, report submissions and record changes (audit logs)</li>
      <li>Data stored in your browser to keep you signed in and remember preferences (login tokens, theme,
        map filters, read alerts). We do not use advertising or tracking cookies.</li>
    </ul>

    <h2>2. How we use your information</h2>
    <ul>
      <li>To create and secure your account and verify your email</li>
      <li>To receive, verify and act on hazard reports, and to show approved hazards on the map</li>
      <li>To provide routing to evacuation centers that avoids reported hazards</li>
      <li>To send you alerts about hazards near you</li>
      <li>To manage evacuation centers, track occupancy, and predict congestion</li>
      <li>To coordinate relief, donations and distribution</li>
      <li>To prepare reports for disaster response and planning (published reports use totals, not names)</li>
      <li>To prevent abuse such as fake accounts and false reports, and to investigate security incidents</li>
    </ul>

    <h2>3. Legal basis for processing</h2>
    <ul>
      <li><strong>Consent</strong>, which you give when you register and when you allow location access</li>
      <li><strong>The PDRRMO's mandate</strong> under the Philippine Disaster Risk Reduction and Management
        Act of 2010 (Republic Act No. 10121) to carry out disaster preparedness and response</li>
      <li><strong>Protection of life and health</strong> of you and others during emergencies</li>
    </ul>

    <h2>4. Who we share it with</h2>
    <p>We do not sell your personal information. We share it only as follows:</p>
    <ul>
      <li><strong>Authorized PDRRMO and municipal (MDRRMO) personnel, response teams and evacuation center
        staff</strong>, limited to the records they need for their role and area.</li>
      <li><strong>Other government agencies</strong> involved in disaster response or relief, when needed to
        protect life or when required by law.</li>
      <li><strong>The public and other users:</strong> once a hazard report is approved, its type, severity,
        location, description and photos may appear on the map. Your name and contact details on the report are
        not shown publicly. <em>[TODO: confirm this matches what the map shows.]</em></li>
      <li><strong>Service providers</strong> that help run the system:
        <table>
          <thead>
            <tr><th>Provider</th><th>Purpose</th><th>Data involved</th></tr>
          </thead>
          <tbody>
            <tr><td>Brevo</td><td>Sending verification and password reset emails</td><td>Email address, one-time code</td></tr>
            <tr><td>Google reCAPTCHA</td><td>Blocking automated sign-ups</td><td>IP address, browser and interaction data</td></tr>
            <tr><td>OpenRouteService</td><td>Calculating evacuation routes</td><td>Route start and end points</td></tr>
            <tr><td>OpenStreetMap / Nominatim</td><td>Map display and turning coordinates into addresses</td><td>Map area viewed, hazard coordinates, IP address</td></tr>
            <tr><td>Cloud hosting and file storage</td><td>Running the system and storing uploaded photos</td><td>All data stored in the system</td></tr>
          </tbody>
        </table>
        Some of these providers process data outside the Philippines. Their use of data is governed by their own
        privacy policies.
      </li>
    </ul>

    <h2>5. How long we keep it</h2>
    <ul>
      <li>Email verification codes: expire after 10 minutes and are deleted once you register</li>
      <li>System audit logs (including IP address and browser): {{ info.auditRetentionDays }} days</li>
      <li>Route request logs: {{ info.routeLogRetentionDays }} days</li>
      <li>Account information: while your account is active, and deleted or anonymized after you ask us to
        close it, unless we must keep it longer by law</li>
      <li>Hazard reports and their review history: {{ info.hazardReportRetention }}, as part of the province's
        disaster records</li>
      <li>Evacuee records: {{ info.evacueeRecordRetention }}, as part of the province's disaster records</li>
    </ul>

    <h2>6. How we protect it</h2>
    <ul>
      <li>Passwords and verification codes are stored hashed, never in plain text</li>
      <li>Connections are encrypted and sign-in sessions expire automatically</li>
      <li>Access is limited by role and municipality, and actions are recorded in audit logs</li>
      <li>Sign-up is protected by email verification and reCAPTCHA</li>
    </ul>
    <p>
      No system is completely secure. Please use a strong password and log out on shared devices. If a breach
      affects your data, we will notify you and the National Privacy Commission as the law requires.
    </p>

    <h2>7. Your rights</h2>
    <p>Under the Data Privacy Act, you have the right to:</p>
    <ul>
      <li><strong>Be informed</strong> about how your data is processed</li>
      <li><strong>Access</strong> the personal data we hold about you</li>
      <li><strong>Correct</strong> inaccurate or outdated data (you can edit most details on your profile page)</li>
      <li><strong>Object</strong> to processing, and <strong>withdraw consent</strong></li>
      <li><strong>Erasure or blocking</strong> of data that is no longer needed or was unlawfully processed</li>
      <li><strong>Data portability</strong>, to get a copy of your data in a common format</li>
      <li><strong>Damages</strong> for harm caused by inaccurate or unlawfully processed data</li>
      <li><strong>File a complaint</strong> with the National Privacy Commission (privacy.gov.ph)</li>
    </ul>
    <p>
      Some records, such as evacuee and hazard records needed for disaster response, may have to be kept even
      if you ask us to delete them. We will tell you if that applies. To exercise any of these rights, contact
      our Data Protection Officer below.
    </p>

    <h2>8. Minors</h2>
    <p>
      If you are under 18, please create an account only with the knowledge and consent of a parent or
      guardian. Information about minors in evacuation centers is recorded by authorized staff for relief
      purposes only.
    </p>

    <h2>9. Changes to this policy</h2>
    <p>
      We may update this policy as the system changes. We will change the effective date above and, for
      significant changes, notify you in the app or by email.
    </p>

    <h2>10. Contact us</h2>
    <p>
      Data Protection Officer: {{ info.dpoName }}<br />
      {{ info.office }}, {{ info.province }}<br />
      {{ info.officeAddress }}<br />
      Email: <a :href="`mailto:${info.dpoEmail}`">{{ info.dpoEmail }}</a><br />
      Phone: {{ info.dpoPhone }}
    </p>
  </LegalLayout>
</template>

<script setup>
import LegalLayout from "@/components/legal/LegalLayout.vue";
import { LEGAL_INFO as info } from "@/data/legalInfo";
</script>