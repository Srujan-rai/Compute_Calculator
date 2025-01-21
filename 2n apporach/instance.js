const inputField = document.getElementById('i6');

if (inputField) {
  inputField.value = 50;
  
  inputField.dispatchEvent(new Event('input', { bubbles: true }));
  
  console.log('Input field updated to:', inputField.value);
} else {
  console.error('Input field not found.');
}
