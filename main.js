/**
 * PetCare+ Core JavaScript Library
 */

document.addEventListener('DOMContentLoaded', function() {
    // 1. Sidebar Toggle
    const sidebar = document.getElementById('sidebar');
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    if (sidebarCollapse && sidebar) {
        sidebarCollapse.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }

    // 2. Initialize Bootstrap Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 3. Client-Side Date Validation Rules
    // Check Next Due Date >= Date Administered
    const adminDateInput = document.getElementById('date_administered');
    const nextDueDateInput = document.getElementById('next_due_date');

    if (adminDateInput && nextDueDateInput) {
        function validateDates() {
            if (adminDateInput.value && nextDueDateInput.value) {
                if (new Date(nextDueDateInput.value) < new Date(adminDateInput.value)) {
                    nextDueDateInput.setCustomValidity("Next due date cannot be earlier than administered date.");
                } else {
                    nextDueDateInput.setCustomValidity("");
                }
            }
        }
        adminDateInput.addEventListener('change', validateDates);
        nextDueDateInput.addEventListener('change', validateDates);
    }

    // Check Start Date <= End Date for Medications
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    if (startDateInput && endDateInput) {
        function validateMedDates() {
            if (startDateInput.value && endDateInput.value) {
                if (new Date(endDateInput.value) < new Date(startDateInput.value)) {
                    endDateInput.setCustomValidity("End date cannot be earlier than start date.");
                } else {
                    endDateInput.setCustomValidity("");
                }
            }
        }
        startDateInput.addEventListener('change', validateMedDates);
        endDateInput.addEventListener('change', validateMedDates);
    }
});
