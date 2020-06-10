let contrast = (hex, bw) => {
    if (hex.indexOf('#') === 0) {
        hex = hex.slice(1);
    }
    // convert 3-digit hex to 6-digits.
    if (hex.length === 3) {
        hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }
    if (hex.length !== 6) {
        throw new Error('Invalid HEX color.');
    }
    var r = parseInt(hex.slice(0, 2), 16),
        g = parseInt(hex.slice(2, 4), 16),
        b = parseInt(hex.slice(4, 6), 16);
    if (bw) {
        // http://stackoverflow.com/a/3943023/112731
        return (r * 0.299 + g * 0.587 + b * 0.114) > 186
            ? '#000000'
            : '#FFFFFF';
    }
    // invert color components
    r = (255 - r).toString(16);
    g = (255 - g).toString(16);
    b = (255 - b).toString(16);
    // pad each with zeros and return
    return "#" + padZero(r) + padZero(g) + padZero(b);
}

let initial = () => {
    color = randomNumber();
    return [color, contrast(color, true)];
}

let randomNumber = () => {
    colors = [
        '#ffebee', '#ffcdd2', '#ef9a9a', '#e57373', '#ef5350', '#f44336', '#e53935', '#d32f2f', '#c62828', '#b71c1c', '#ff8a80', '#ff5252', '#ff1744', '#d50000', '#fce4ec', '#f8bbd0', '#f48fb1', '#f06292', '#ec407a', '#e91e63', '#d81b60', '#c2185b', '#ad1457', '#880e4f', '#ff80ab', '#ff4081', '#f50057', '#c51162', '#f3e5f5', '#e1bee7', '#ce93d8', '#ba68c8', '#ab47bc', '#9c27b0', '#8e24aa', '#7b1fa2', '#6a1b9a', '#4a148c', '#ea80fc', '#e040fb', '#d500f9', '#aa00ff', '#ede7f6', '#d1c4e9', '#b39ddb', '#9575cd', '#7e57c2', '#673ab7', '#5e35b1', '#512da8', '#4527a0', '#311b92', '#b388ff', '#7c4dff', '#651fff', '#6200ea', '#e8eaf6', '#c5cae9', '#9fa8da', '#7986cb', '#5c6bc0', '#3f51b5', '#3949ab', '#303f9f', '#283593', '#1a237e', '#8c9eff', '#536dfe', '#3d5afe', '#304ffe', '#e3f2fd', '#bbdefb', '#90caf9', '#64b5f6', '#42a5f5', '#2196f3', '#1e88e5', '#1976d2', '#1565c0', '#0d47a1', '#82b1ff', '#448aff', '#2979ff', '#2962ff', '#e1f5fe', '#b3e5fc', '#81d4fa', '#4fc3f7', '#29b6f6', '#03a9f4', '#039be5', '#0288d1', '#0277bd', '#01579b', '#80d8ff', '#40c4ff', '#00b0ff', '#0091ea', '#e0f7fa', '#b2ebf2', '#80deea', '#4dd0e1', '#26c6da', '#00bcd4', '#00acc1', '#0097a7', '#00838f', '#006064', '#84ffff', '#18ffff', '#00e5ff', '#00b8d4', '#e0f2f1', '#b2dfdb', '#80cbc4', '#4db6ac', '#26a69a', '#009688', '#00897b', '#00796b', '#00695c', '#004d40', '#a7ffeb', '#64ffda', '#1de9b6', '#00bfa5', '#e8f5e9', '#c8e6c9', '#a5d6a7', '#81c784', '#66bb6a', '#4caf50', '#43a047', '#388e3c', '#2e7d32', '#1b5e20', '#b9f6ca', '#69f0ae', '#00e676', '#00c853', '#f1f8e9', '#dcedc8', '#c5e1a5', '#aed581', '#9ccc65', '#8bc34a', '#7cb342', '#689f38', '#558b2f', '#33691e', '#ccff90', '#b2ff59', '#76ff03', '#64dd17', '#f9fbe7', '#f0f4c3', '#e6ee9c', '#dce775', '#d4e157', '#cddc39', '#c0ca33', '#afb42b', '#9e9d24', '#827717', '#f4ff81', '#eeff41', '#c6ff00', '#aeea00', '#fffde7', '#fff9c4', '#fff59d', '#fff176', '#ffee58', '#ffeb3b', '#fdd835', '#fbc02d', '#f9a825', '#f57f17', '#ffff8d', '#ffff00', '#ffea00', '#ffd600', '#fff8e1', '#ffecb3', '#ffe082', '#ffd54f', '#ffca28', '#ffc107', '#ffb300', '#ffa000', '#ff8f00', '#ff6f00', '#ffe57f', '#ffd740', '#ffc400', '#ffab00', '#fff3e0', '#ffe0b2', '#ffcc80', '#ffb74d', '#ffa726', '#ff9800', '#fb8c00', '#f57c00', '#ef6c00', '#e65100', '#ffd180', '#ffab40', '#ff9100', '#ff6d00', '#fbe9e7', '#ffccbc', '#ffab91', '#ff8a65', '#ff7043', '#ff5722', '#f4511e', '#e64a19', '#d84315', '#bf360c', '#ff9e80', '#ff6e40', '#ff3d00', '#dd2c00', '#efebe9', '#d7ccc8', '#bcaaa4', '#a1887f', '#8d6e63', '#795548', '#6d4c41', '#5d4037', '#4e342e', '#3e2723', '#fafafa', '#f5f5f5', '#eeeeee', '#e0e0e0', '#bdbdbd', '#9e9e9e', '#757575', '#616161', '#424242', '#212121',
    ];
    return colors[parseInt(Math.random() * (colors.length - 0) + 0)];
}

let delete_model = (self, parent, csrfmiddlewaretoken = $('meta[name=csrf]').attr("content")) => {
    let alert = $('div.response')
    $.ajax({
        url: $(self).attr('url'),
        data: {
            csrfmiddlewaretoken,
            _method: 'delete',
        },
        method: 'POST',
        dataType: 'json',
        success: function (data) {
            // console.log(data.comments);
            if (data.success) {
                html = '' +
                    '<div class="alert alert-success alert-dismissible fade show" role="alert">' +
                    '<strong>!You did it!</strong> You stop the container ' + data.object.name + '.' +
                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                    '<span aria-hidden="true">&times;</span>' +
                    '</button>' +
                    '</div>'
                alert.html('')
                alert.html(html)
                $('#' + parent).remove()
            }
        },

        beforeSend: function () {
            html = '' +
                '<div class="alert alert-info alert-dismissible fade show" role="alert">' +
                '<div class="row justify-content-between">' +
                '<div class="col-11">' +
                '<strong>!We are working on it!</strong> Your request is being processed' +
                '</div>' +
                '<div class="col-1 text-right">' +
                '<i class="fas fa-circle-notch fa-pulse"></i>' +
                '</div>' +
                '</div>' +
                '</div>'
            alert.html(html)
        }

    });
}

let stop_model = (self, csrfmiddlewaretoken = $('meta[name=csrf]').attr("content")) => {
    let alert = $('div.response')
    $.ajax({
        url: $(self).attr('url'),
        data: {
            csrfmiddlewaretoken,
            _method: 'put',
        },
        method: 'POST',
        dataType: 'json',
        success: function (data) {
            // console.log(data.comments);
            if (data.success) {
                html = '' +
                    '<div class="alert alert-success alert-dismissible fade show" role="alert">' +
                    '<strong>!You did it!</strong> You stop the container ' + data.object.name + '.' +
                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                    '<span aria-hidden="true">&times;</span>' +
                    '</button>' +
                    '</div>'
                alert.html('')
                alert.html(html)

                new_icon = '' +
                    '<i url="/module/' + data.object.id + '"' +
                    'method="put" onclick="click_model(this, i' + data.object.id + 'Confirm request, ¿You want to delete the container?)"' +
                    'class="fas fa-play-circle pointer text-primary" ' +
                    'data-toggle="tooltip" ' +
                    'data-placement="bottom" ' +
                    'title="Start model"' +
                    '></i>'
                $(self).after(new_icon)
                $(self).remove()
            }
        },

        beforeSend: function () {
            html = '' +
                '<div class="alert alert-info alert-dismissible fade show" role="alert">' +
                '<div class="row justify-content-between">' +
                '<div class="col-11">' +
                '<strong>!We are working on it!</strong> Your request is being processed' +
                '</div>' +
                '<div class="col-1 text-right">' +
                '<i class="fas fa-circle-notch fa-pulse"></i>' +
                '</div>' +
                '</div>' +
                '</div>'
            alert.html(html)
        }
    });
}

let modalConstruct = (titulo, mensaje) => {
    modal = '' +
        '<div class="modal fade" id="exampleModalCenter" tabindex="-1" role="dialog" aria-labelledby="exampleModalCenterTitle" aria-hidden="true">' +
        '<div class="modal-dialog modal-dialog-centered" role="document">' +
        '<div class="modal-content">' +
        '<div class="modal-header">' +
        '<h5 class="modal-title" id="exampleModalLongTitle">' + titulo + '</h5>' +
        '<button type="button" class="close" data-dismiss="modal" aria-label="Close">' +
        '<span aria-hidden="true">&times;</span>' +
        '</button>' +
        '</div>' +
        '<div class="modal-body">' +
        mensaje +
        '</div>' +
        '<div class="modal-footer">' +
        '<button type="button" class="btn btn-danger" id="modal-btn-si">Si</button>' +
        '<button type="button" class="btn btn-default" id="modal-btn-no">No</button>' +
        '</div>'
    '</div>' +
        '</div>' +
        '</div>';
    return modal;
}

let newModal = (titulo, mensaje, insert_in = $('#modal')) => {
    insert_in.html(modalConstruct(titulo, mensaje));
    $('#exampleModalCenter').modal('show');
}

let modalConfirm = (titulo, mensaje, callback) => {
    newModal(titulo, mensaje);
    $("#modal-btn-si").on("click", function () {
        callback(true);
        $("#exampleModalCenter").modal('hide');
    });
    $("#modal-btn-no").on("click", function () {
        callback(false);
        $("#exampleModalCenter").modal('hide');

    });
}

const actions_model = (self, parent) => {
    switch ($(self).attr('method')) {
        case 'delete':
            delete_model(self, parent)
            break;

        case 'put':
            stop_model(self)
            break;

        default:
            alert("metodo no configurado")
            break;
    }
}

let click_model = (self, parent, title, message) => {
    modalConfirm(
        title,
        message,
        function (confirm) {
            $("#exampleModalCenter").modal('hide');
            if (confirm) {
                actions_model(self, parent)
            }
        }
    )
}