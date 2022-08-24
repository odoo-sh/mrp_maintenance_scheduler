odoo.define('mrp_maintenance_scheduler.compute_duration', function (require) {
    "use strict";
    
var fields = require('web.basic_fields');
var field_registry = require('web.field_registry');
var fieldUtils = require('web.field_utils');
var time = require('web.time');

    
var StepTimeCounter  = fields.FieldFloatTime.extend({
    
    init: function () {
        this._super.apply(this, arguments);
        this.duration = this.record.data.duration;
    },

    willStart: function () {
        var self = this;
        var def = this._rpc({
            model: 'maitenance.request.duration',
            method: 'search_read',
            domain: [
                ['maintenance_step_id', '=', this.record.data.id],
                ['date_end', '=', false],
            ],
        }).then(function (result) {
            var currentDate = new Date();
            var duration = 0;
            if (result.length > 0) {
                duration += self._getDateDifference(time.auto_str_to_date(result[0].date_start), currentDate);
            }
            var minutes = duration / 60 >> 0;
            var seconds = duration % 60;
            self.duration += minutes + seconds / 60;
            if (self.mode === 'edit') {
                self.value = self.duration;
            }
        });
        return Promise.all([this._super.apply(this, arguments), def]);
    },

    destroy: function () {
        this._super.apply(this, arguments);
        clearTimeout(this.timer);
    },
    isSet: function () {
        return true;
    },
    _getDateDifference: function (dateStart, dateEnd) {
        return moment(dateEnd).diff(moment(dateStart), 'seconds');
    },
    
    _renderReadonly: function () {
        if (this.record.data.is_user_working) {
            this._startTimeCounter();
        } else {
            this._super.apply(this, arguments);
        }
    },
    
    _startTimeCounter: function () {
        var self = this;
        clearTimeout(this.timer);
        if (this.record.data.is_user_working) {
            this.timer = setTimeout(function () {
                self.duration += 1/60;
                self._startTimeCounter();
            }, 1000);
        } else {
            clearTimeout(this.timer);
        }
        this.$el.text(fieldUtils.format.float_time(this.duration));
        },
    }); 


    field_registry.add('step_time_counter', StepTimeCounter);
    fieldUtils.format.step_time_counter = fieldUtils.format.float_time;
    
return StepTimeCounter;
    });
    