function closeModalAndShowPrevious() {
    // Close the current modal (editProfileModal)
    let currentModal = bootstrap.Modal.getInstance(document.querySelector('#editProfileModal'));
    currentModal.hide();

    // Open the previous modal (profileModal)
    let previousModal = document.getElementById('profileModal');
    let modalInstance = new bootstrap.Modal(previousModal);
    modalInstance.show();
}
