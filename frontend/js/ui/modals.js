// render functions for modals

const modalContainer = document.getElementById("modal");
const modalContent = document.getElementById("modal-content");


export const openModal = (data, renderer) => {
    modalContainer.classList.remove("hidden");
    renderer(data, modalContent);
};

export const closeModal = () => {
    modalContainer.classList.add("hidden");
};

