function closeModal() {
    const modal = document.getElementById('modal');
    if (modal) {
        modal.classList.add('opacity-0');
        setTimeout(() => {
            document.getElementById('modal-container').innerHTML = '';
        }, 200);
    }
}

// Make it globally available
window.closeModal = closeModal;
