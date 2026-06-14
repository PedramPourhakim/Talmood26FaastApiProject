module.exports = {
  content: [
    "./templates/**/*.html",
    "./app/**/*.py",
  ],
  theme: {
    extend: {},
  },
  plugins: [
      require('@tailwindcss/forms'),
  ],
}
// npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
//npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css
//npm install @tailwindcss/forms