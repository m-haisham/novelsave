<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="stylesheet" href="assets/css/bootstrap.min.css">
        <title>${novel.title}</title>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4 shadow-sm">
            <div class="container">
                <a class="navbar-brand me-1" href="">${novel.title}</a>
            </div>
        </nav>

        <main class="container">
            <div class="card mb-4">
                <div class="list-group list-group-flush">
                    <div class="list-group-item">
                        <div class="row flex-column flex-md-row">
                            <div class="col-12 col-md-3 fw-bold">Author:</div>
                            <div class="col ms-2 ms-md-0">${novel.author}</div>
                        </div>
                    </div>
                    % for label, values in metadata.items():
                    <div class="list-group-item">
                        <div class="row flex-column flex-md-row">
                            <div class="col-12 col-md-3 fw-bold">${label.capitalize()}</div>
                            <div class="col ms-2 ms-md-0">${', '.join(values)}</div>
                        </div>
                    </div>
                    % endfor
                    <div class="list-group-item">
                        <div class="row flex-column flex-md-row">
                            <div class="col-12 col-md-3 fw-bold">Sources:</div>
                            <div class="col ms-2 ms-md-0">
                                ${', '.join(sources)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card mb-4">
                <div class="card-header fw-bold">Synopsis</div>
                <div class="card-body">
                    % for line in novel.synopsis.splitlines():
                    <p>${line}</p>
                    % endfor
                </div>
            </div>

            <div class="card mb-4">
                <div class="card-header fw-bold d-flex justify-content-between align-items-center">
                    Chapters
                    <span class="badge bg-secondary">${chapter_count}</span>
                </div>
                <ul class="list-group list-group-flush">
                    % if not has_sections:
                    % for chapter_wrapper in volume_wrappers[0]['chapter_wrappers']:
                        <a class="list-group-item list-group-item-action" href="chapters/${chapter_wrapper.get('filename')}">
                            ${chapter_wrapper['chapter'].title}
                        </a>
                    % endfor
                    % else:
                    % for volume_wrapper in volume_wrappers:
                        <button
                            class="
                                list-group-item list-group-item-action
                                d-flex
                                justify-content-between
                                align-items-center
                            "
                            type="button"
                            data-bs-toggle="collapse"
                            data-bs-target="#${volume_wrapper['id']}"
                            aria-expanded="false"
                            aria-controls="volume"
                        >
                            ${volume_wrapper['volume'].name}
                            <span class="badge bg-secondary">${len(volume_wrapper['chapter_wrappers'])}</span>
                        </button>
                        <ul class="list-group list-group-flush collapse" id="${volume_wrapper['id']}">
                        % for chapter_wrapper in volume_wrapper['chapter_wrappers']:
                            <a class="list-group-item list-group-item-action" href="chapters/${chapter_wrapper.get('filename')}">
                                ${chapter_wrapper['chapter'].title}
                            </a>
                        % endfor
                        </ul>
                    % endfor
                    % endif
                </ul>
            </div>
        </main>
        <script src="assets/js/bootstrap.min.js"></script>
    </body>
</html>
