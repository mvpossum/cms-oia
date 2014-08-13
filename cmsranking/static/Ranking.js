/* Programming contest management system
 * Copyright © 2012 Luca Wehrstedt <luca.wehrstedt@gmail.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */

if (!window.console) {
    window.console = new Object();
}

if (!window.console.log) {
    window.console.log = function () {};
}

if (!window.console.info) {
    window.console.info = function () {};
}

if (!window.console.warn) {
    window.console.warn = function () {};
}

if (!window.console.error) {
    window.console.error = function () {};
}

$(document).ready(function() {
    DataStore.init(function(){
        HistoryStore.init();
        UserDetail.init();
        TimeView.init();
        TeamSearch.init();
        Overview.init();
        Scoreboard.init("1");
        $("#Nivel1").css('background', '#00cc00');
    });
	$("#Nivel1").click(function (event) {
        Scoreboard.generate("1");
        $("#Nivel1").css('background', '#00cc00');
        $("#Nivel2").css('background', '');
        $("#Nivel3").css('background', '');
        $("#NivelX").css('background', '');
	});
	$("#Nivel2").click(function (event) {
        Scoreboard.generate("2");
        $("#Nivel1").css('background', '');
        $("#Nivel2").css('background', '#00cc00');
        $("#Nivel3").css('background', '');
        $("#NivelX").css('background', '');
	});
	$("#Nivel3").click(function (event) {
        Scoreboard.generate("3");
        $("#Nivel1").css('background', '');
        $("#Nivel2").css('background', '');
        $("#Nivel3").css('background', '#00cc00');
        $("#NivelX").css('background', '');
	});
	$("#NivelX").click(function (event) {
        Scoreboard.generate("x");
        $("#Nivel1").css('background', '');
        $("#Nivel2").css('background', '');
        $("#Nivel3").css('background', '');
        $("#NivelX").css('background', '#00cc00');
	});
});
