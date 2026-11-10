<template>
  <LegalLayout title="Terms of Service" :effective-date="info.termsEffectiveDate">
    <p>
      These Terms govern your use of {{ info.appName }}, operated by the {{ info.office }} of
      {{ info.province }} ("PDRRMO", "we", "us"). By creating an account or using the system, you agree to these
      Terms and to our <router-link to="/privacy">Privacy Policy</router-link>. If you do not agree, please do
      not use {{ info.appName }}.
    </p>

    <div class="legal-callout">
      <strong>In an emergency, call 911 or your local emergency hotline first.</strong>
      {{ info.appName }} is a support tool. It does not replace official warnings, evacuation orders, or
      instructions from authorities and responders on the ground.
    </div>

    <h2>1. What {{ info.appName }} does</h2>
    <p>
      {{ info.appName }} shows evacuation center locations, suggests routes that avoid reported hazards,
      estimates how crowded centers may become, lets residents report hazards, and helps authorized personnel
      manage evacuation centers, evacuees and donations.
    </p>

    <h2>2. Your account</h2>
    <ul>
      <li>Give accurate, current information and keep it up to date.</li>
      <li>Create only one account, for yourself. Do not register on behalf of someone else without their
        permission.</li>
      <li>Keep your password private. You are responsible for activity under your account. Tell us right away
        if you think someone else has used it.</li>
      <li>If you are under 18, use {{ info.appName }} only with a parent's or guardian's consent.</li>
    </ul>

    <h2>3. Hazard reports</h2>
    <ul>
      <li>Report only hazards you believe in good faith are real, and describe them as accurately as you can.</li>
      <li>Upload only photos you took or have the right to share. Avoid showing people's faces, injured persons,
        or private information unless it is needed to describe the hazard.</li>
      <li>Reports are reviewed by authorized personnel and may be approved, dismissed, edited for clarity, or
        removed. Approved reports may be shown to other users and on the public map.</li>
      <li>By submitting a report, you allow the PDRRMO and partner agencies to use its contents, including
        photos, for disaster response, public safety alerts, and records.</li>
    </ul>

    <h2>4. What you must not do</h2>
    <ul>
      <li>Submit false, prank, or misleading reports. These can send responders to the wrong place and put
        lives at risk.</li>
      <li>Impersonate another person, official, or agency.</li>
      <li>Upload content that is unlawful, obscene, threatening, or that violates someone's privacy.</li>
      <li>Try to access accounts, records, or areas of the system you are not authorized to use.</li>
      <li>Interfere with the system, bypass security checks such as reCAPTCHA or email verification, or overload
        it with automated requests or scraping.</li>
      <li>Use the system or its data for commercial, political, or any purpose other than disaster preparedness
        and response.</li>
    </ul>
    <p>
      Misuse may lead to suspension or removal of your account, and may be reported to the proper authorities
      where the law applies.
    </p>

    <h2>5. Additional rules for staff and administrators</h2>
    <p>If you have a staff, response team, or administrator account, you also agree to:</p>
    <ul>
      <li>Access and change records only as your official duties require.</li>
      <li>Keep evacuee and reporter information confidential, and never copy, export, or share it outside
        authorized channels.</li>
      <li>Enter accurate data, as other responders and reports rely on it.</li>
      <li>Report any suspected data breach or misuse to the Data Protection Officer immediately.</li>
    </ul>
    <p>Your actions in the system are logged.</p>

    <h2>6. Accuracy and availability</h2>
    <ul>
      <li>Routes, hazard information, center capacity and congestion forecasts are based on the data available
        and may be incomplete, delayed, or wrong. Roads may be blocked by hazards that have not been reported.
        Always use your own judgment and follow instructions from authorities.</li>
      <li>Congestion predictions are estimates, not guarantees that space is available.</li>
      <li>Map data comes from third parties such as OpenStreetMap and may not reflect current conditions.</li>
      <li>The system may be slow or unavailable, especially during disasters when power and mobile networks are
        affected. We may also pause it for maintenance.</li>
    </ul>

    <h2>7. Limitation of liability</h2>
    <p>
      {{ info.appName }} is provided "as is" as a public service. To the extent allowed by law, the PDRRMO and
      the system's developers are not liable for any loss or injury resulting from reliance on information in
      the system, from its unavailability, or from content submitted by other users. Nothing in these Terms
      limits any liability that cannot be limited under Philippine law.
    </p>

    <h2>8. Suspension and closing your account</h2>
    <p>
      We may suspend or deactivate accounts that break these Terms or that appear compromised. You may ask us to
      close your account at any time by contacting us below. Records needed for disaster response may be kept
      as described in our <router-link to="/privacy">Privacy Policy</router-link>.
    </p>

    <h2>9. Changes to these Terms</h2>
    <p>
      We may update these Terms. We will change the effective date above and, for significant changes, notify
      you in the app or by email. Continuing to use {{ info.appName }} after changes means you accept them.
    </p>

    <h2>10. Governing law</h2>
    <p>These Terms are governed by the laws of the Republic of the Philippines.</p>

    <h2>11. Contact us</h2>
    <p>
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