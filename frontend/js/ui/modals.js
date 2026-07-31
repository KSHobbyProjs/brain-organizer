// render functions for modals

const modalContainer = document.getElementById("modal");
const modalContent = document.getElementById("modal-content");

// TODO: Use this const settingsContainer = document.getElementById("settings-modal");

export const openModal = (data, renderer) => {
    modalContainer.classList.remove("hidden");
    renderer(data, modalContent);
};

export const closeModal = () => {
    modalContainer.classList.add("hidden");
};
